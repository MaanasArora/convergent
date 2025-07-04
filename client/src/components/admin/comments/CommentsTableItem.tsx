import { Input } from "@headlessui/react";
import { type ModerationComment } from "../../../app/core/dashboard";
import { StatusPill } from "../../ui/StatusPill";
import { useQuery } from "@tanstack/react-query";
import { putApi } from "../../api/base";

export const CommentsTableItem = ({
  comment: comment,
  onComplete,
}: {
  comment: ModerationComment;
  onComplete?: Function;
}) => {
  async function handleApprove() {
    await approveComment.refetch();
    if (onComplete) {
      onComplete();
    }
  }

  async function handleReject() {
    await rejectComment.refetch();
    if (onComplete) {
      onComplete();
    }
  }

  const approveComment = useQuery({
    queryKey: [`comment-approve-${comment.id}`],
    queryFn: () => putApi(`/moderation/comments/${comment.id}/approve`),
    enabled: false,
  });

  const rejectComment = useQuery({
    queryKey: [`comment-reject-${comment.id}`],
    queryFn: () => putApi(`/moderation/comments/${comment.id}/reject`),
    enabled: false,
  });

  return (
    <tr className="items-center">
      <td className="p-5">
        <Input type="checkbox" className="h-5 w-5" />
      </td>
      <td className="p-5 w-full">
        <strong>{comment.id}</strong>
        <br />
        {comment.content}
      </td>
      <td className="p-5">
        <StatusPill moderationStatus={comment.approved} />
      </td>
      <td className="p-5">
        <div className="flex gap-4">
          {!comment.approved && (
            <button
              className="border-2 px-2 py-2 rounded-xl flex flex-row items-center gap-x-2 h-min self-center-safe border-green-800 bg-green-100 hover:bg-green-800 hover:text-white"
              onClick={handleApprove}
            >
              Approve
            </button>
          )}

          {(comment.approved === null || !!comment.approved) && (
            <button
              className="border-2 px-2 py-2 rounded-xl flex flex-row items-center gap-x-2 h-min self-center-safe border-red-800 bg-red-100 hover:bg-red-800 hover:text-white"
              onClick={handleReject}
            >
              Reject
            </button>
          )}
        </div>
      </td>
    </tr>
  );
};
