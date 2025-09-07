import { useQuery } from "@tanstack/react-query";
import { useCallback, useEffect, useMemo } from "react";
import { useParams } from "react-router";
import { getApi } from "../../components/api/base";
import {
  createVote,
  getConversation,
  getConversationIdByFriendlyName,
  getNextComment,
} from "../../components/api/conversation";
import { ParticipationSpa } from "../../components/participation/ParticipationSpa";
import type { Conversation, ParticipationComment } from "./dashboard";

const ConversationPage = () => {
  const params = useParams<{ conversationId: string;}>();
  const conversationIdOrName = params.conversationId;
  // This controls max. time (in s) the user need to wait before they can see the new comment(s)
  // TODO: make it configurable (server level? conversation level?)
  const autoRefetchInterval = 15;

  const friendlyId = useQuery({
    queryKey: ["conversation-id-name", conversationIdOrName || ""],
    queryFn: () => getConversationIdByFriendlyName(conversationIdOrName || ""),
    retry: false,
    enabled: !!conversationIdOrName,
  });

  const conversationId = useMemo(() => {
    return friendlyId.data || conversationIdOrName;
  }, [friendlyId.data, conversationIdOrName]);

  const conversation = useQuery<Conversation>({
    queryKey: ["current-conversation", conversationId],
    queryFn: () => getConversation(conversationId ?? ""),
    retry: false,
    refetchInterval: autoRefetchInterval * 1000,
  });

  const currentComment = useQuery<{
    comment: ParticipationComment;
    num_votes: number;
  }>({
    queryKey: ["current-comment", conversationId],
    queryFn: () => getNextComment(conversationId ?? ""),
    retry: false,
    refetchInterval: autoRefetchInterval * 1000,
  });

  const nextComment = useCallback(async () => {
    if (!conversationId) return;

    await currentComment.refetch();
  }, [conversationId, currentComment]);

  const fetchConversation = useCallback(async () => {
    if (!conversationId) return;
    await conversation.refetch();
  }, [conversationId, conversation]);

  // dialog logic
  // biome-ignore lint/correctness/useExhaustiveDependencies: Run on load
  useEffect(() => {
    const fetchData = async () => {
      await fetchConversation();
      await nextComment();
    };
    fetchData();
  }, []);

  const onFormComplete = () => {
    comments.refetch();
  };
  // end of dialog logic

  const onVote = async (
    commentId: string,
    vote: "agree" | "disagree" | "skip",
  ) => {
    const voteNum = vote === "agree" ? 1 : vote === "disagree" ? -1 : 0;

    if (!conversationId) return;
    await createVote(commentId, voteNum);
    await nextComment();
  };

  const allCommentsVoted = useMemo(() => {
    return !!currentComment.error?.message;
  }, [currentComment]);

  const comments = useQuery<[]>({
    queryKey: [`comment-query-${conversationId}`],
    queryFn: () => getApi(`/conversations/${conversationId}/comments`),
  });
  return (
    <ParticipationSpa
      conversation={conversation.data}
      currentComment={allCommentsVoted ? undefined : currentComment.data}
      comments={comments.data}
      onVoteComplete={onVote}
      onComplete={onFormComplete}
    />
  );
};

export default ConversationPage;
