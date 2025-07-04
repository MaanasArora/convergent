import { useQuery } from "@tanstack/react-query";
import { getApi } from "../api/base";
import { useParams } from "react-router";
import CommentsTable from "../admin/comments/CommentsTable";
import { useEffect, useState } from "react";
import CommentConfig from "../admin/comments/CommentConfig";

export default function ManageComments() {
  const params = useParams();

  const convoId = params.conversationId;
  const comments = useQuery<[]>({
    queryKey: [`comment-query-${convoId}`],
    queryFn: () => getApi(`/moderation/conversations/${convoId}/comments`),
  });

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
    comments.refetch();
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
      <CommentsTable
        onComplete={onFormComplete}
        comments={comments.data ?? []}
      />
      {!!convoId && (
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
          <CommentConfig onComplete={onFormComplete} conversationId={convoId} />
        </dialog>
      )}
    </section>
  );
}
