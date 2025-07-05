import { useQuery } from "@tanstack/react-query";
import { getApi } from "../api/base";
import { useParams } from "react-router";
import CommentsTable from "../admin/comments/CommentsTable";
import { ModerationComment } from "../../app/core/dashboard";

export default function ManageComments() {
  let params = useParams();

  const convoId = params.conversationId;
  const comments = useQuery<ModerationComment[]>({
    queryKey: [`comment-query-${convoId}`],
    queryFn: () => getApi(`/moderation/conversations/${convoId}/comments`),
  });

  const onFormComplete = () => {
    comments.refetch();
  };

  return (
    <CommentsTable
      conversationId={convoId}
      comments={comments.data ?? []}
      onComplete={onFormComplete}
    />
  );
}
