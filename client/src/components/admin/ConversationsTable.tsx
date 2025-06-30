import { Input } from "@headlessui/react";
import { Conversation } from "../../app/core/dashboard";
import dayjs from "dayjs";

const StatusPill = ({ isActive }: { isActive: boolean }) => {
  return (
    <div
      className={`px-3 py-1 rounded-full whitespace-nowrap font-semibold w-fit ${
        isActive ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"
      }`}
    >
      &bull; &nbsp;
      {isActive ? "Active" : "Inactive"}
    </div>
  );
};

export const ConversationTable = ({
  conversations,
}: {
  conversations: Conversation[];
}) => {
  return (
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
            <ConversationTableItem conversation={conversation} />
          ))}
        </tbody>
      </table>
    </div>
  );
};

const ConversationTableItem = ({
  conversation,
}: {
  conversation: Conversation;
}) => {
  const viewLink = `/conversation/${conversation.id}`;
  const editLink = `/conversation/${conversation.id}/edit`;

  return (
    <tr className="items-center">
      <td className="p-5">
        <Input type="checkbox" className="h-5 w-5" />
      </td>
      <td className="p-5">
        <strong>{conversation.name}</strong>
        <br />
        {conversation.description}
      </td>
      <td className="p-5">{conversation.num_participants}</td>
      <td className="p-5">
        {dayjs(conversation.date_created).format("MMM D, YYYY")}
      </td>
      <td className="p-5">
        <StatusPill isActive={conversation.is_active} />
      </td>
      <td className="p-5">
        <span className="text-gray-600">{conversation.author.username}</span>
      </td>
      <td className="p-5 flex gap-4">
        <a href={viewLink} className="text-gray-800 hover:underline">
          View
        </a>
        <a href={editLink} className="text-gray-800 hover:underline">
          Edit
        </a>
      </td>
    </tr>
  );
};
