import CoreBase from "./base";
import ConversationsList from "../../components/conversation/ConversationList";

export type Conversation = {
  id: string;
  name: string;
  description: string;
  author: { username: string };
  num_participants: number;
  date_created: string;
  is_active: boolean;
};

const DashboardPage = () => {
  return (
    <CoreBase>
      <ConversationsList />
    </CoreBase>
  );
};

export default DashboardPage;
