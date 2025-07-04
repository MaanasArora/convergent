import { useState } from "react";
import { postApi, putApi } from "../../api/base";

export default function CommentConfig({
  conversationId,
  editId,
  onComplete,
}: {
  conversationId: string;
  editId?: string;
  onComplete?: Function;
}) {
  const [comment, setComment] = useState("");
  async function formSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    // const formData = new FormData(event.target as HTMLFormElement);
    const newConversationRequestBody = {
      content: comment,
    };
    if (!editId) {
      // new conversation
      await postApi(
        `/conversations/${conversationId}/comments`,
        newConversationRequestBody
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
  return (
    <form onSubmit={formSubmit}>
      <h2 className="text-3xl font-bold my-4">New comment</h2>
      <textarea
        className="border-gray-500 border-2"
        name="description"
        id="description"
        value={comment}
        onChange={(event) => setComment(event.target.value)}
      ></textarea>
      <button className="border-2 px-2 py-2 rounded-xl flex flex-row items-center gap-x-2 ml-auto">
        Submit
      </button>
    </form>
  );
}
