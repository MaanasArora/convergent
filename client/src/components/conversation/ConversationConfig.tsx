import { Input, Textarea } from "@headlessui/react";
import { ArrowLeftIcon } from "@heroicons/react/24/solid";
import { useState } from "react";
import { useNavigate } from "react-router";
import type { Conversation } from "../../app/core/dashboard";
import { postApi, putApi } from "../api/base";

export default function ConversationConfig({
  editItem,
  type,
  onComplete,
}: {
  editItem?: Conversation;
  type?: string;
  onComplete?: () => void;
}) {
  const navigate = useNavigate();

  // const [conversationId, setConversationId] = useState(editItem?.id ?? "");

  const [conversationName, setConversationName] = useState(
    editItem?.name ?? "",
  );
  const [conversationDescription, setConversationDescription] = useState(
    editItem?.description ?? "",
  );

  const [
    conversationAllowUnmoderatedComments,
    setConversationAllowUnmoderatedComments,
  ] = useState(editItem?.display_unmoderated ?? false);

  const [conversationShowCharts, setConversationShowCharts] = useState(
    editItem?.show_charts ?? false,
  ); // TODO: placeholder; change to correct value later

  const [conversationAllowVotes, setConversationAllowVotes] = useState(
    editItem?.allow_votes ?? false,
  ); // TODO: placeholder; change to correct value later
  // const [updated, setUpdated] = useState(0);

  const [conversationFriendlyLink, setConversationFriendlyLink] = useState(
    editItem?.user_friendly_link ?? "",
  );

  async function formSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const formData = new FormData(event.target as HTMLFormElement);
    const newConversationRequestBody = {
      display_unmoderated: formData.get("display-unmoderated") === "on",
      show_charts: formData.get("show-charts") === "on", // TODO: placeholder; change to correct value later
      allow_votes: formData.get("allow-votes") === "on", // TODO: placeholder; change to correct value later
      user_friendly_link: formData.get("user-friendly-link"), // TODO: placeholder; change to correct value later
      name: formData.get("name"),
      description: formData.get("description"),
    };
    if (!editItem)
      // new conversation
      await postApi("/conversations", newConversationRequestBody);
    // .then((resp) => {
    //   setConversationId(resp.id);
    // });
    else {
      // edit conversation
      await putApi(
        `/conversations/${editItem?.id}`,
        newConversationRequestBody,
      );
      // .then(
      //   (resp) => {
      //     setUpdated(Date.now());
      //     setConversationId(resp.id);
      //   }
      // );
    }
    if (onComplete) {
      onComplete();
    }
    if (type !== "dialog") {
      navigate("/home");
    }
  }

  return (
    <div className="flex flex-col items-start h-full py-4 w-[95%] max-w-3xl mx-auto">
      <div className="flex flex-row w-full gap-4 items-center">
        {!editItem && (
          <a
            type="button"
            className="h-12 p-3 aspect-square w-max rounded-full hover:bg-red-800 hover:text-white bg-gray-200"
            title="back"
            href="/conversation"
            // onClick={() => handleEditClick(false)}
          >
            <span className="w-4">
              <ArrowLeftIcon />
            </span>
          </a>
        )}

        <hgroup>
          <h1 className="text-5xl font-bold">
            {editItem ? "Edit conversation" : "Create conversation"}
          </h1>
          <p>
            Add in copy that allows people to understand what creating a
            conversation does.
          </p>
        </hgroup>
      </div>
      <form
        method={type}
        onSubmit={formSubmit}
        id="conversation-form"
        className="w-full flex flex-col"
      >
        <fieldset className="flex flex-col mx-auto gap-2 w-full">
          <label htmlFor="name">Conversation Heading</label>
          <Input
            className="border-gray-500 border-2 rounded-md p-2"
            type="text"
            name="name"
            id="name"
            placeholder="Title here"
            required
            value={conversationName}
            onChange={(event) => setConversationName(event.target.value)}
          ></Input>
          <label htmlFor="description">Description for conversation</label>
          <Textarea
            className="border-gray-500 border-2 rounded-md p-2"
            name="description"
            id="description"
            placeholder="Description here"
            value={conversationDescription}
            onChange={(event) => setConversationDescription(event.target.value)}
          ></Textarea>
        </fieldset>
        {!editItem && (
          <div className="col-span-2 text-center">Seed Comment Placeholder</div>
        )}

        <fieldset>
          <legend className="font-bold text-2xl">Setup Permissions</legend>
          <label htmlFor="show-charts" className="flex gap-2 p-2">
            <Input
              className="border-gray-500 border-2 justify-self-start aspect-square h-6"
              type="checkbox"
              name="show-charts"
              id="show-charts"
              checked={conversationShowCharts}
              onChange={(event) =>
                setConversationShowCharts(event.target.checked)
              }
            ></Input>
            Participants can see visualization
          </label>
          <label htmlFor="display-unmoderated" className="flex gap-2 p-2">
            <Input
              className="border-gray-500 border-2 justify-self-start aspect-square h-6"
              type="checkbox"
              name="display-unmoderated"
              id="display-unmoderated"
              checked={conversationAllowUnmoderatedComments}
              onChange={(event) =>
                setConversationAllowUnmoderatedComments(event.target.checked)
              }
            ></Input>
            No comments shown without moderator approval
          </label>
          <label htmlFor="allow-votes" className="flex gap-2 p-2">
            <Input
              className="border-gray-500 border-2 justify-self-start aspect-square h-6"
              type="checkbox"
              name="allow-votes"
              id="allow-votes"
              checked={conversationAllowVotes}
              onChange={(event) =>
                setConversationAllowVotes(event.target.checked)
              }
            ></Input>
            Make Conversation Open
          </label>
          <label htmlFor="user-friendly-link" className="flex gap-2 p-2">
            Use Custom Link for Conversation
            <Input
              className="border-gray-500 border-2 justify-self-start aspect-square h-6"
              name="user-friendly-link"
              id="user-friendly-link"
              value={conversationFriendlyLink}
              onChange={(event) =>
                setConversationFriendlyLink(event.target.value)
              }
            ></Input>
          </label>
        </fieldset>

        <button
          type="submit"
          className="self-center border-2 border-gray-500 hover:border-green-500 p-2 bg-gray-500 hover:bg-green-500 text-white rounded-xl"
        >
          {editItem ? "Save" : "Create conversation"}
        </button>
      </form>
    </div>
  );
}
