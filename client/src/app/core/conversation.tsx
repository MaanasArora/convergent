import { useParams } from "react-router";
import CoreBase from "./base";
import {
  createVote,
  getConversation,
  getNextComment,
} from "../../components/api/conversation";
import { useEffect, useMemo, useState } from "react";
import {
  CheckIcon,
  ForwardIcon,
  PlusIcon,
  XMarkIcon,
} from "@heroicons/react/24/solid";
import { Button } from "@headlessui/react";
import { Conversation } from "./dashboard";
import { useQuery } from "@tanstack/react-query";
import { getApi } from "../../components/api/base";
import CommentConfig from "../../components/admin/comments/CommentConfig";

type Comment = { content: string; id: string; num_votes: number };

const VotingSection = ({
  comment,
  commentNumber,
  onVote,
}: {
  comment: Comment | null;
  commentNumber?: number;
  onVote: (commentId: string, vote: "agree" | "disagree" | "skip") => void;
}) => {
  return (
    comment && (
      <div className="flex flex-col items-start gap-4 p-4 bg-white rounded-xl">
        <div className="flex flex-col items-start gap-2 mb-2">
          <h3 className="font-semibold">Comment {commentNumber}</h3>
          <p className="text-gray-700 text-2xl font-bold">{comment.content}</p>
          <time className="text-gray-500">(time here)</time>
        </div>
        <div className="flex items-center gap-2 w-full">
          <Button
            onClick={() => onVote(comment.id, "agree")}
            className="border hover:bg-primary hover:text-white px-2 py-2 rounded-xl flex flex-row items-center gap-x-2"
          >
            <CheckIcon className="h-5 w-5" />
            Agree
          </Button>
          <Button
            onClick={() => onVote(comment.id, "disagree")}
            className="border hover:bg-primary hover:text-white px-2 py-2 rounded-xl flex flex-row items-center gap-x-2"
          >
            <XMarkIcon className="h-5 w-5" />
            Disagree
          </Button>
          <Button
            onClick={() => onVote(comment.id, "skip")}
            className="bg-background px-2 py-2 rounded-xl flex flex-row items-center gap-x-2 border border-gray-300 text-gray-700 hover:bg-primary hover:text-white ml-auto"
          >
            Skip
            <ForwardIcon className="h-5 w-5" />
          </Button>
        </div>
      </div>
    )
  );
};

const ConversationPage = () => {
  const { conversationId } = useParams<{ conversationId: string }>();

  const conversation = useQuery<Conversation>({
    queryKey: ["current-conversation", conversationId],
    queryFn: () => getConversation(conversationId ?? ""),
  });

  const currentComment = useQuery<{ comment: Comment; num_votes: number }>({
    queryKey: ["current-comment", conversationId],
    queryFn: () => getNextComment(conversationId ?? ""),
  });

  const amountOfVotedComments = useMemo(() => {
    return currentComment.data?.num_votes ?? 0;
  }, [currentComment]);
  const nextComment = async () => {
    if (!conversationId) return;

    await currentComment.refetch();
  };
  const fetchConversation = async () => {
    if (!conversationId) return;
    await conversation.refetch();
  };

  // dialog logic
  useEffect(() => {
    const fetchData = async () => {
      await fetchConversation();
      await nextComment();
    };
    fetchData();
  }, [conversationId]);

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
  // end of dialog logic

  const onVote = async (
    commentId: string,
    vote: "agree" | "disagree" | "skip"
  ) => {
    const voteNum = vote === "agree" ? 1 : vote === "disagree" ? -1 : 0;

    if (!conversationId) return;
    await createVote(commentId, voteNum);
    await nextComment();
  };

  const comments = useQuery<[]>({
    queryKey: [`comment-query-${conversationId}`],
    queryFn: () => getApi(`/conversations/${conversationId}/comments`),
  });
  return (
    <CoreBase>
      <main className="w-[95%] mx-auto">
        <section className="p-8">
          <h1 className="text-3xl font-bold mb-4">{conversation.data?.name}</h1>
          <p className="mb-4">{conversation.data?.description}</p>
        </section>
        <section
          className="p-8 bg-background w-full flex flex-col"
          aria-labelledby="active-comment-header"
        >
          <div className="flex justify-between items-center">
            <h2
              id="active-comment-header"
              className="font-semibold text-secondary mb-4"
            >
              Active Comments
            </h2>
            <Button
              onClick={() => handleEditClick(true)}
              className="flex mb-4 bg-white border border-gray-300 p-2 w-min whitespace-nowrap items-center justify-center gap-x-2 rounded-xl"
            >
              <PlusIcon height={30} width={30} /> Add Comment
            </Button>
          </div>

          {currentComment.isSuccess ? (
            <VotingSection
              comment={currentComment.data?.comment}
              commentNumber={amountOfVotedComments + 1}
              onVote={onVote}
            />
          ) : (
            <div className="flex flex-col items-center justify-center p-4 bg-white rounded-xl">
              <p className="text-gray-500">No more comments to review.</p>
            </div>
          )}
          <p className="text-center pt-6">
            {amountOfVotedComments + 1} of {comments.data?.length} comments
          </p>
        </section>
      </main>
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
    </CoreBase>
  );
};

export default ConversationPage;
