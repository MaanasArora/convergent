import type { Meta, StoryObj } from "@storybook/react-vite";

import CommentsTable from "./CommentsTable";

const meta = {
  title: "client/admin/Comments Table",
  component: CommentsTable,
  argTypes: {
    comments: { control: "object" },
  },
} satisfies Meta<typeof CommentsTable>;

export default meta;
type Story = StoryObj<typeof meta>;

export const NoComment: Story = {
  args: {
    conversationId: "d035d428-90c1-4ea9-99de-1d7c1f81a939",
    comments: [],
  },
};

export const SomeComments: Story = {
  args: {
    conversationId: "d035d428-90c1-4ea9-99de-1d7c1f81a939",
    comments: [
      {
        id: "fbeec989-d824-410d-9577-2f235e688b01",
        content: "test1",
        user_id: "162f507e-7f6e-4871-a8c8-4912c3be624c",
        approved: null,
      },
      {
        id: "32ac0523-464e-4e11-8382-d9e3a6680db3",
        content: "test2",
        user_id: "162f507e-7f6e-4871-a8c8-4912c3be624c",
        approved: true,
      },
      {
        id: "0f55d2fd-2717-4bbb-b0e9-bff72e7c83e6",
        content: "",
        user_id: "162f507e-7f6e-4871-a8c8-4912c3be624c",
        approved: false,
      },
    ],
  },
};
