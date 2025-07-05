import type { Meta, StoryObj } from "@storybook/react-vite";
import { ConversationsTable } from "./ConversationsTable";

const meta = {
  title: "client/admin/Conversation Table",
  component: ConversationsTable,
  argTypes: {
    conversations: { control: "object" },
  },
} satisfies Meta<typeof ConversationsTable>;

export default meta;
type Story = StoryObj<typeof meta>;

export const NoConversation: Story = {
  args: {
    conversations: [],
  },
};

export const SomeConversations: Story = {
  args: {
    conversations: [
      {
        id: "d035d428-90c1-4ea9-99de-1d7c1f81a939",
        name: "Title test",
        description: "desc",
        author: {
          id: "162f507e-7f6e-4871-a8c8-4912c3be624c",
          username: "gg@gg.ca",
        },
        num_participants: 1,
        date_created: "2025-07-04T04:38:18.318536",
        is_active: true,
        display_unmoderated: false,
      },
    ],
  },
};
