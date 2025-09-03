import { useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import type { Conversation } from "../../app/core/dashboard";
import { deleteApi } from "../api/base";
import ConversationConfig from "./ConversationConfig";

export default function ConversationDialog({
  onComplete,
  editIdItem,
}: {
  onComplete: () => void;
  editIdItem: Conversation;
}) {
  const [dialog, setDialog] = useState<HTMLDialogElement | null>(null);
  useEffect(() => {
    // const editButton = document.getElementById("edit-button");
    setDialog(document.getElementById("edit-dialog") as HTMLDialogElement);
  }, []);

  const handleEditClick = (state: boolean) => {
    if (state) {
      dialog?.showModal();
    } else {
      dialog?.close();
    }
  };

  const onFormComplete = () => {
    dialog?.close();
    if (onComplete) onComplete();
  };

  return (
    <>
      <button
        type="button"
        id="edit-button"
        className="border-2 px-2 py-2 rounded-xl flex flex-row items-center gap-x-2 h-min self-center-safe"
        onClick={() => handleEditClick(true)}
      >
        Edit
      </button>
      <dialog
        id="edit-dialog"
        className="m-[revert] p-[revert] border-2 backdrop:bg-primary backdrop:opacity-80 rounded-xl"
      >
        <div className="top-bar flex justify-between">
          {editIdItem && <DeleteConfig conversation={editIdItem} />}
          <button
            type="button"
            className="border-1 border-gray-300 px-2 py-2 rounded-xl flex flex-row items-center gap-x-2 ml-auto"
            onClick={() => handleEditClick(false)}
          >
            Close
          </button>
        </div>
        <ConversationConfig
          editItem={editIdItem}
          type="dialog"
          onComplete={onFormComplete}
        />
      </dialog>
    </>
  );
}

function DeleteConfig({ conversation }: { conversation: Conversation }) {
  const [dialog, setDialog] = useState<HTMLDialogElement | null>(null);
  useEffect(() => {
    // const editButton = document.getElementById("edit-button");
    setDialog(
      document.getElementById(
        "delete-conversation-dialog",
      ) as HTMLDialogElement,
    );
  }, []);
  const handleEditClick = (state: boolean) => {
    if (state) {
      dialog?.showModal();
    } else {
      dialog?.close();
    }
  };

  const navigate = useNavigate();

  const deleteConversation = useQuery<{ detail: string; id: string }>({
    queryKey: [`delete-conversation-${conversation.id}`],
    queryFn: () => deleteApi(`/conversations/${conversation.id}`),
    enabled: false,
  });

  const onFormComplete = () => {
    deleteConversation.refetch();
  };

  useEffect(() => {
    if (
      deleteConversation.data?.detail === "Conversation deleted successfully"
    ) {
      navigate("/home");
    }
  }, [deleteConversation.data, navigate]);
  return (
    <>
      <button
        type="button"
        className="w-min border-2 border-red-500 p-2 bg-red-200 hover:bg-red-500 hover:text-white rounded-xl"
        onClick={() => handleEditClick(true)}
      >
        Delete
      </button>
      <dialog
        id="delete-conversation-dialog"
        className="m-[revert] p-[revert] backdrop:bg-primary backdrop:opacity-80 rounded-xl"
      >
        <button
          type="button"
          className="border-1 border-gray-300 px-2 py-2 rounded-xl flex flex-row items-center gap-x-2 ml-auto"
          onClick={() => handleEditClick(false)}
        >
          Close
        </button>
        <hgroup className="py-4">
          <h1 className="text-4xl font-bold my-4">
            Deleting this conversation?
          </h1>
          <p>
            Your conversation, <em>{conversation.name}</em>, will be deleted
          </p>
          <p>So does ALL comments, voting records & related data.</p>
        </hgroup>

        <div className="w-full flex justify-between">
          <button
            type="button"
            className="border-2 border-red-500 p-2 bg-red-200 hover:bg-red-500 hover:text-white rounded-xl"
            onClick={onFormComplete}
          >
            Delete the conversation
          </button>
          <button
            type="button"
            className="border-2 px-2 py-2 rounded-xl flex flex-row items-center gap-x-2 h-min self-center-safe"
            onClick={() => handleEditClick(false)}
          >
            Cancel
          </button>
        </div>
      </dialog>
    </>
  );
}
