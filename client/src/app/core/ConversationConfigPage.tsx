import { Outlet, useParams } from "react-router";
import ConversationConfig from "../../components/conversation/ConversationConfig";
import CoreBase from "./base";
import { useQuery } from "@tanstack/react-query";
import { useEffect } from "react";
import { getApi } from "../../components/api/base";
import { Conversation } from "./dashboard";
import ManageConversation from "../../components/conversation/ManageConversation";

const ConversationConfigPage = () => {
  const params = useParams();

  const editId = params.conversationId;
  const editIdItem = useQuery<Conversation>({
    queryKey: [""],
    queryFn: () => getApi(`/conversations/${editId}`),
    enabled: false,
  });

  useEffect(() => {
    if (editId) {
      refetchData();
    }
  }, [editId]);

  const refetchData = () => {
    editIdItem.refetch();
  };

  return (
    <CoreBase requiresLogin={true}>
      {editId ? (
        editIdItem.data ? (
          <>
            <ManageConversation
              editIdItem={editIdItem.data}
              refetch={refetchData}
            />
            <Outlet />
          </>
        ) : (
          <section>Loading...</section>
        )
      ) : (
        <ConversationConfig />
      )}
    </CoreBase>
  );
};

export default ConversationConfigPage;
