import CoreBase from "./base";
import ConversationsList from "../../components/conversation/ConversationsList";

export type Conversation = {
  id: string;
  name: string;
  description: string;
  author: { username: string };
  num_participants: number;
  date_created: string;
  is_active: boolean;
};

export type Comment = {
  id: string;
  content: string;
};

export type ModerationComment = Comment & {
  user_id: string;
  approved: boolean | null;
};

const DashboardPage = () => {
  return (
    <CoreBase requiresLogin={true}>
      <ConversationsList />
    </CoreBase>
  );
};

export default DashboardPage;
