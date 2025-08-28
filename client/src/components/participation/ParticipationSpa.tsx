import { useEffect, useMemo, useState } from "react";
import CoreBase from "../../app/core/base";
import type {
  Comment,
  Conversation,
  ParticipationComment,
} from "../../app/core/dashboard";
import { NewCommentDialog } from "../admin/comments/CommentDialog";
import { VotingSection } from "./VotingSection";

export const ParticipationSpa = ({
  conversation,
  currentComment,
  comments,
  onVoteComplete,
  onComplete,
}: {
  conversation?: Conversation;
  currentComment?: {
    comment: ParticipationComment;
    num_votes: number;
  };
  comments?: Comment[];
  onVoteComplete: (
    commentId: string,
    vote: "agree" | "disagree" | "skip",
  ) => void;
  onComplete: (event?: React.FormEvent<HTMLFormElement>) => void;
}) => {
  const [dialog, setDialog] = useState<HTMLDialogElement | null>(null);

  const amountOfVotedComments = useMemo(() => {
    return currentComment?.num_votes ?? 0;
  }, [currentComment]);

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
  const onVote = (commentId: string, vote: "agree" | "disagree" | "skip") => {
    if (onVoteComplete) {
      onVoteComplete(commentId, vote);
    }
  };
  const onFormComplete = (event?: React.FormEvent<HTMLFormElement>) => {
    handleEditClick(false);

    if (onComplete) {
      onComplete(event);
    }
  };

  return (
    <CoreBase>
      <main className="w-[95%] mx-auto">
        <section className="p-8">
          <h1 className="text-3xl font-bold mb-4">{conversation?.name}</h1>
          <p className="mb-4">{conversation?.description}</p>
        </section>
        <section
          className="p-8 bg-background w-full xl:w-1/2 flex flex-col"
          aria-labelledby="active-comment-header"
        >
          <div className="flex justify-between items-center">
            <h2
              id="active-comment-header"
              className="font-semibold text-secondary mb-4"
            >
              Active Comments
            </h2>
            {!!conversation && (
              <NewCommentDialog
                conversation={conversation}
                onComplete={onFormComplete}
              />
            )}
          </div>

          {currentComment ? (
            <VotingSection
              comment={currentComment.comment}
              commentNumber={amountOfVotedComments + 1}
              onVote={onVote}
            />
          ) : (
            <div className="flex flex-col items-center justify-center p-4 bg-white rounded-xl">
              <p className="text-gray-500">No more comments to review.</p>
            </div>
          )}
          {!!currentComment && (
            <p className="text-center pt-6">
              {amountOfVotedComments + 1} of {comments?.length} comments
            </p>
          )}
        </section>
      </main>
    </CoreBase>
  );
};
