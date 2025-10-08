import { FunnelIcon } from "@heroicons/react/24/outline";
import { useMemo, useState } from "react";
import type {
  Conversation,
  ModerationComment,
} from "../../../app/core/dashboard";
import { NewCommentDialog } from "./CommentDialog";
import { CommentsTableItem } from "./CommentsTableItem";
import { CSVLink } from "react-csv";

const mappedState = new Map([
  ["unmoderated", null],
  ["approved", true],
  ["rejected", false],
]);
export default function CommentsTable({
  comments,
  conversation,
  onComplete,
}: {
  comments: ModerationComment[];
  conversation?: Conversation;
  onComplete?: () => void;
}) {
  const [filter, setFilter] = useState<string[]>([]);

  const transpose = comments.map(comment => [comment.user_id, comment.approved, comment.content]);
  const dataCsv = [
    ["UserID", "ModerationState", "Content"],
    ...transpose,
  ];

  const onFilterChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const toggledValue = e.target.value;
    if (filter.includes(toggledValue)) {
      setFilter(filter.filter((name) => name !== toggledValue));
    } else if (toggledValue === "all") {
      setFilter(filter.filter(() => false));
    } else {
      setFilter(filter.concat([toggledValue]));
    }
  };

  const filteredComments = useMemo(() => {
    // if (filter.length === 0) return comments;
    const filteredModes = filter.map((item) =>
      mappedState.get(item)?.toString(),
    );

    return comments
      .filter((item) =>
        filteredModes.length === 0
          ? true
          : filteredModes.includes(item.approved?.toString()),
      )
      .sort((a, b) => {
        if (a.approved === null && b.approved === null) {
          return 0;
        }
        if (a.approved === null) {
          return -1;
        }
        if (b.approved === null) {
          return 1;
        }
        return 0;
      });
  }, [comments, filter]);

  return (
    <section className="w-[95%] max-w-4xl mx-auto">
      <div className="py-2 flex justify-between">
        <div className='flex gap-x-4 items-center'>
          <details className="[&:open>summary]:rounded-b-none [&:open>summary]:border-b-transparent relative">
            <summary className="border-2 px-2 py-2 rounded-xl flex flex-row items-center gap-x-2 w-min cursor-pointer">
              Filter <FunnelIcon className="h-8 w-8" />
            </summary>
            <form className="flex flex-col border-2 absolute bg-white p-4 rounded-b-xl rounded-tr-xl w-max">
              <label>
                <input
                  type="checkbox"
                  value="all"
                  checked={filter.length === 0}
                  onChange={onFilterChange}
                ></input>
                All
              </label>
              <label>
                <input
                  type="checkbox"
                  value="unmoderated"
                  checked={filter.includes("unmoderated")}
                  onChange={onFilterChange}
                ></input>
                Unmoderated
              </label>
              <label>
                <input
                  type="checkbox"
                  value="approved"
                  checked={filter.includes("approved")}
                  onChange={onFilterChange}
                ></input>
                Approved
              </label>
              <label>
                <input
                  type="checkbox"
                  value="rejected"
                  checked={filter.includes("rejected")}
                  onChange={onFilterChange}
                ></input>
                Rejected
              </label>
            </form>
          </details>
          <CSVLink data={dataCsv} filename={"conversation.csv"} target="_blank">
            <button className='p-2 bg-secondary text-white rounded-md'>
              Export CSV
            </button>
        </CSVLink>
        </div>
        {!!conversation && (
          <NewCommentDialog
            conversation={conversation}
            onComplete={onComplete}
          />
        )}
      </div>
      <div>
      </div>
      {(filteredComments || []).map((item) => (
        <CommentsTableItem
          comment={item}
          onComplete={onComplete}
          key={item.id}
        />
      ))}
    </section>
  );
}
