import { Input } from "@headlessui/react";
import { Conversation } from "../../../app/core/dashboard";
import { ConversationsTableItem } from "./ConversationsTableItem";

export const ConversationsTable = ({
  conversations,
}: {
  conversations?: Conversation[];
}) => {
  return (
    <div className="flex flex-col items-start h-full w-[85%] mx-auto py-10">
      <div id="heading" className="flex w-full justify-between flex-wrap">
        <div id="heading-text">
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
      {conversations && (
        <div className="border border-gray-200 rounded-2xl shadow-lg w-full min-w-min">
          <table id="conversation-table" className="w-full border-collapse">
            <thead>
              <tr className="text-gray-500 items-center bottom-2 border-b-gray-200 border-b">
                <th className="text-left p-5">
                  <Input type="checkbox" className="h-5 w-5" />
                </th>
                <th className="text-left p-5">Conversation Title</th>
                <th className="text-left p-5">Number of Participants</th>
                <th className="text-left p-5">Date Created</th>
                <th className="text-left p-5">Status</th>
                <th className="text-left p-5">Created By</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {conversations.map((conversation) => (
                <ConversationsTableItem conversation={conversation} />
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
