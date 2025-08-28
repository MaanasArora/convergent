import { useState } from "react";
import type { Conversation } from "../../../app/core/dashboard";
import { postApi } from "../../api/base";

export default function CommentConfig({
  conversation,
  editId,
  onComplete,
  onCancel,
}: {
  conversation: Conversation;
  editId?: string;
  onComplete?: () => void;
  onCancel?: () => void;
}) {
  const [comment, setComment] = useState("");
  const [isHovering, setIsHovering] = useState(false);
  
  async function formSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    // const formData = new FormData(event.target as HTMLFormElement);
    const newConversationRequestBody = {
      content: comment,
    };
    if (!editId) {
      // new conversation
      await postApi(
        `/conversations/${conversation.id}/comments`,
        newConversationRequestBody,
      );
      setComment("");
    } else {
      // edit conversation
      //   putApi(`/conversations/${editItem?.id}`, newConversationRequestBody).then(
      //     (resp) => {
      //       //   setUpdated(Date.now());
      //       //   setConversationId(resp.id);
      //     }
      //   );
    }
    if (onComplete) {
      onComplete();
    }
  }

  function onFormCancel() {
    if (onCancel) {
      onCancel();
    }
  }
  return (
    <form onSubmit={formSubmit} className="flex flex-col gap-4 p-4">
      <h2 className="text-3xl font-bold">Add comment to conversation</h2>
      <p>Add help hints here for creating a comment </p>
      <hgroup className="flex flex-col gap-4">
        <h3 className="text-2xl font-bold">{conversation.name}</h3>
        <p>{conversation.description}</p>
      </hgroup>
      <textarea
        className="border-gray-300 border-2 w-full rounded-md p-2 min-h-40"
        name="description"
        id="description"
        title="description"
        value={comment}
        placeholder="Enter a comment..."
        onChange={(event) => setComment(event.target.value)}
      ></textarea>
      <div className="flex gap-2 my-4 flex-wrap">
        <button
          type="button"
          className="p-2 border-1 border-gray-400 rounded-md hover:bg-red-800 hover:border-red-800 hover:text-white flex-1"
          onClick={onFormCancel}
        >
          Cancel
        </button>
        <div
          className="relative flex-1"
          onMouseEnter={() => setIsHovering(true)}
          onMouseLeave={() => setIsHovering(false)}
        >
          <button
            type="submit"
            className={`px-2 py-1 bg-gray-500 text-white rounded-md w-full ${comment.trim() === "" ? "cursor-default" : "bg-secondary"}`}
            disabled={comment.trim() === ""} 
          >
            Add Comment
          </button>
        </div>
        {comment.trim() === "" && isHovering && (
          <div 
            className="absolute -bottom-12 left-1/2 -translate-x-1/2 bg-white border border-gray-300 rounded-md shadow px-3 py-1 text-sm text-gray-700 z-50 transition-opacity duration-300 ease-in-out"
            role="tooltip"
            aria-live="polite"
          >
            Comment is empty
          </div>
        )}
      </div>
    </form>
  );
}
