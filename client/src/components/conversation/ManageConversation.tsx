import { useQuery } from "@tanstack/react-query";
import { useMemo } from "react";
import { NavLink } from "react-router";
import type { Conversation, ModerationComment } from "../../app/core/dashboard";
import { getApi } from "../api/base";
import BreadCrumb from "../ui/BreadCrumb";
import ConversationDialog from "./ConversationDialog";

export default function ManageConversation({
  editIdItem,
  refetch,
}: {
  editIdItem: Conversation;
  refetch: () => void;
}) {
  const comments = useQuery<ModerationComment[]>({
    queryKey: [`comment-query-${editIdItem.id}`],
    queryFn: () =>
      getApi(`/moderation/conversations/${editIdItem.id}/comments`),
  });

  const unmoderatedCommentsCount = useMemo(() => {
    return (comments.data ?? []).filter((item) => item.approved === null)
      .length;
  }, [comments.data]);

  const onFormComplete = () => {
    if (refetch) refetch();
  };
  return (
    <section className="w-[95%] max-w-4xl mx-auto">
      <BreadCrumb conversation={editIdItem.name} />
      <div className="title flex justify-between">
        <h1 className="text-4xl font-bold my-4">
          Conversation: {editIdItem.name}
        </h1>
        <ConversationDialog
          onComplete={onFormComplete}
          editIdItem={editIdItem}
        />
      </div>

      {!!editIdItem.description && <p>{editIdItem.description}</p>}

      <nav className="border-b-2 flex">
        <NavLink
          className="p-4 flex items-center gap-2 [&.active]:border-b-2"
          to="moderate"
        >
          Moderate
          <div className="px-3 py-1 rounded-full whitespace-nowrap font-semibold w-fit bg-gray-100">
            {unmoderatedCommentsCount}
          </div>
        </NavLink>
        <NavLink
          className="p-4 flex items-center gap-2 [&.active]:border-b-2"
          to="monitor"
        >
          Monitor
        </NavLink>
        <NavLink
          className="p-4 flex items-center gap-2 [&.active]:border-b-2"
          to="distribute"
        >
          Distribute
        </NavLink>
      </nav>
    </section>
  );
}
