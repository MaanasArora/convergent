import { type ModerationComment } from "../../../app/core/dashboard";
import { CommentsTableItem } from "./CommentsTableItem";

export default function CommentsTable({
  comments,
  onComplete,
}: {
  comments: ModerationComment[];
  onComplete?: Function;
}) {
  return (
    <>
      {(comments || []).map((item) => (
        <CommentsTableItem comment={item} onComplete={onComplete} />
      ))}
    </>
  );
}
