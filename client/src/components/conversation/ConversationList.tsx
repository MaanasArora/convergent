import { useQuery } from "@tanstack/react-query";
import { Conversation } from "../../app/core/dashboard";
import { getApi } from "../api/base";
import { ConversationTable } from "../admin/ConversationsTable";

export default function ConversationsList() {
  const conversations = useQuery<Conversation[]>({
    queryKey: ["conversations"],
    queryFn: () => getApi("/conversations"),
  });
  return (
    <div className="flex flex-col items-start h-full w-[85%] mx-auto py-10">
      <div id="heading" className="flex w-full justify-between flex-wrap">
        <div id="hdeading-text">
          <h1 className="text-5xl font-bold mb-8">Conversations</h1>
          <h2 className="mb-16">Find all conversations created below.</h2>
        </div>
        <a
          className="mb-8 px-5 py-3 bg-secondary text-white rounded-md h-fit"
          href="/conversation/new"
        >
          + Create conversation
        </a>
      </div>
      {conversations.data && (
        <ConversationTable conversations={conversations.data} />
      )}
    </div>
  );
}
