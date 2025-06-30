import { useParams } from "react-router";
import ConversationConfig from "../../components/conversation/ConversationConfig";
import CoreBase from "./base";
import { useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { getApi } from "../../components/api/base";
import { Conversation } from "./dashboard";
import ManageConversation from "../../components/conversation/ManageConversation";

const ConversationConfigPage = () => {
  let params = useParams();

  const editId = params.conversationId;

  const [conversationName, setConversationName] = useState("");
  const [conversationDescription, setConversationDescription] = useState("");

  if (editId) {
    const editIdItem = useQuery<Conversation>({
      queryKey: [""],
      queryFn: () => getApi(`/conversations/${editId}`),
    }).data;
    useEffect(() => {
      if (editIdItem) {
        setConversationName(editIdItem.name);
        setConversationDescription(editIdItem.description);
      }
    }, [editIdItem]);

    if (editId) {
      return (
        <CoreBase>
          {editIdItem ? (
            <ManageConversation editIdItem={editIdItem} />
          ) : (
            <section>Loading...</section>
          )}
        </CoreBase>
      );
    }
  }

  return (
    <CoreBase>
      <ConversationConfig />
    </CoreBase>
  );
};

export default ConversationConfigPage;
