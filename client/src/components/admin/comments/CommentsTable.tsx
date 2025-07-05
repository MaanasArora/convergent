import { useEffect, useState } from "react";
import { type ModerationComment } from "../../../app/core/dashboard";
import { CommentsTableItem } from "./CommentsTableItem";
import CommentConfig from "./CommentConfig";

export default function CommentsTable({
  comments,
  conversationId,
  onComplete,
}: {
  comments: ModerationComment[];
  conversationId?: string;
  onComplete?: Function;
}) {
  const [dialog, setDialog] = useState<HTMLDialogElement | null>(null);
  useEffect(() => {
    setDialog(document.getElementById("comment-dialog") as HTMLDialogElement);
  }, []);

  const handleEditClick = (state: boolean) => {
    if (state) {
      dialog?.showModal();
    } else {
      dialog?.close();
    }
  };

  const onFormComplete = () => {
    handleEditClick(false);

    if (onComplete) {
      onComplete();
    }
  };

  return (
    <section className="w-[95%] max-w-3xl mx-auto">
      <div className="title flex justify-between">
        <h2 className="text-3xl font-bold my-4">Comments</h2>
        <button
          className="border-2 px-2 py-2 rounded-xl flex flex-row items-center gap-x-2 h-min self-center-safe"
          onClick={() => handleEditClick(true)}
        >
          Add
        </button>
      </div>
      {(comments || []).map((item) => (
        <CommentsTableItem comment={item} />
      ))}
      {!!conversationId && (
        <dialog
          id="comment-dialog"
          className="m-[revert] p-[revert] border-2 backdrop:bg-primary backdrop:opacity-80"
        >
          <button
            className="border-2 px-2 py-2 rounded-xl flex flex-row items-center gap-x-2 ml-auto"
            autoFocus
            onClick={() => handleEditClick(false)}
          >
            Close
          </button>
          <CommentConfig
            onComplete={onFormComplete}
            conversationId={conversationId}
          />
        </dialog>
      )}
    </section>
  );
}
