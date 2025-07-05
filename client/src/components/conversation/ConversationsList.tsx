import { useQuery } from "@tanstack/react-query";
import { Conversation } from "../../app/core/dashboard";
import { getApi } from "../api/base";
import { ConversationsTable } from "../admin/conversations/ConversationsTable";

export default function ConversationsList() {
  const conversations = useQuery<Conversation[]>({
    queryKey: ["conversations"],
    queryFn: () => getApi("/moderation/conversations"),
  });
  return <ConversationsTable conversations={conversations.data} />;
}
