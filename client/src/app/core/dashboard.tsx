import CoreBase from "./base";
import ConversationsList from "../../components/conversation/ConversationsList";

// see server\convergent\routers\conversation.py
export type Conversation = {
  id: string;
  name: string;
  description: string;
  author: { username: string };
  num_participants: number;
  date_created: string;
  is_active: boolean;
  display_unmoderated: boolean;
};

export type Comment = {
  id: string;
  content: string;
};

// See server\convergent\routers\moderation.py
export type ModerationComment = Comment & {
  user_id: string;
  approved: boolean | null;
};

const DashboardPage = () => {
  return (
    <CoreBase>
      <ConversationsList />
    </CoreBase>
  );
};

export default DashboardPage;
