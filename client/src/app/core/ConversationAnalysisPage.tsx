import { useParams } from "react-router";
import CoreBase from "./base";
import { useQuery } from "@tanstack/react-query";
import { getApi } from "../../components/api/base";
import dayjs from "dayjs";
import { Conversation } from "./dashboard";

interface CommentAnalysis {
  id: string;
  content: string;
  consensus: number;
  representativeness: number;
  agree_percentage: number;
}

interface GroupAnalysis {
  group_id: number;
  users: string[];
  representative_comments: CommentAnalysis[];
}

interface ConversationAnalysis {
  user_ids: string[];
  comment_ids: string[];
  comments_by_consensus: CommentAnalysis[];
  groups: GroupAnalysis[];
}

export default function ConversationAnalysisPage() {
  const params = useParams();

  const conversationId = params.conversationId;

  const conversationResponse = useQuery({
    queryKey: ["conversation", conversationId],
    queryFn: () => getApi(`/conversations/${conversationId}`),
    enabled: !!conversationId,
  });
  const conversation = conversationResponse.data as Conversation;

  const conversationAnalysisResponse = useQuery({
    queryKey: ["conversation-analysis", conversationId],
    queryFn: () => getApi(`/analysis/conversation/${conversationId}`),
    enabled: !!conversationId,
  });
  const conversationAnalysis =
    conversationAnalysisResponse.data as ConversationAnalysis;

  if (
    conversationResponse.isLoading ||
    conversationAnalysisResponse.isLoading
  ) {
    return (
      <CoreBase requiresLogin={true}>
        <div className="flex justify-center items-center h-64">
          <div className="text-gray-500">Loading analysis...</div>
        </div>
      </CoreBase>
    );
  }

  return (
    <CoreBase requiresLogin={true}>
      <section className="xl:w-[90%] w-full mx-auto p-5">
        <h1 className="text-3xl font-bold mb-2">{conversation.name}</h1>
        <h2 className="text-xl font-semibold mb-8">Conversation Analysis</h2>
        <div className="mb-4">
          <h2 className="text-xl font-semibold mb-2">Summary</h2>
          <p>
            <strong>Description:</strong> {conversation.description}
          </p>
          <p>
            <strong>Created By:</strong> {conversation.author.username}
          </p>
          <p>
            <strong>Created At:</strong>{" "}
            {dayjs(conversation.date_created).format("MMMM D, YYYY h:mm A")}
          </p>
          <p>
            <strong>Total Participants:</strong>{" "}
            {conversationAnalysis.user_ids.length || 0}
          </p>
          <p>
            <strong>Total Comments:</strong>{" "}
            {conversationAnalysis.comment_ids.length || 0}
          </p>
        </div>
        <div className="mb-8">
          <h2 className="text-xl font-semibold mb-2">Groups</h2>
          <p className="mb-4">
            From the participants in this conversation,{" "}
            <strong>{conversationAnalysis.groups.length}</strong> groups emerged
            based on their response patterns.
          </p>
          <table className="min-w-full border border-gray-300">
            <thead>
              <tr className="bg-gray-200">
                <th className="border border-gray-300 px-4 py-2 text-left">
                  Group ID
                </th>
                <th className="border border-gray-300 px-4 py-2 text-left">
                  Number of Members
                </th>
              </tr>
            </thead>
            <tbody>
              {conversationAnalysis.groups.map((group) => (
                <tr key={group.group_id}>
                  <td className="border border-gray-300 px-4 py-2">
                    Group {group.group_id}
                  </td>
                  <td className="border border-gray-300 px-4 py-2">
                    {group.users.length}
                  </td>
                </tr>
              ))}
              {conversationAnalysis.groups.length === 0 && (
                <tr>
                  <td
                    colSpan={2}
                    className="border border-gray-300 px-4 py-2 text-center"
                  >
                    No groups identified.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        <div>
          <h2 className="text-xl font-semibold mb-2">Consensus</h2>
          <p className="mb-4">
            Below are the comments in the conversation ranked by their consensus
            scores. Higher scores indicate greater agreement across groups,
            while lower scores suggest the comment is more divisive.
          </p>
          <table className="min-w-full border border-gray-300">
            <thead>
              <tr className="bg-gray-200">
                <th className="border border-gray-300 px-4 py-2 text-left w-1/12">
                  Rank
                </th>
                <th className="border border-gray-300 px-4 py-2 text-left w-1/2">
                  Comment
                </th>
                <th className="border border-gray-300 px-4 py-2 text-left w-5/12">
                  Consensus Score
                </th>
              </tr>
            </thead>
            <tbody>
              {conversationAnalysis.comments_by_consensus.map(
                (comment, index) => (
                  <tr key={comment.id}>
                    <td className="border border-gray-300 px-4 py-2">
                      {index + 1}
                    </td>
                    <td className="border border-gray-300 px-4 py-2">
                      {comment.content}
                    </td>
                    <td className="border border-gray-300 px-4 py-2">
                      <div className="flex items-center">
                        <div className="relative w-64 h-4 bg-gray-200 rounded">
                          <div
                            className={
                              "absolute top-0 left-0 h-full rounded bg-green-500"
                            }
                            style={{ width: `${comment.consensus * 100}%` }}
                          />
                        </div>
                        <span className="ml-2 text-sm">
                          {` (${comment.consensus.toFixed(2)})`}
                        </span>
                      </div>
                    </td>
                  </tr>
                ),
              )}
              {conversationAnalysis.comments_by_consensus.length === 0 && (
                <tr>
                  <td
                    colSpan={2}
                    className="border border-gray-300 px-4 py-2 text-center"
                  >
                    No comments available for analysis.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        <div className="mt-8">
          <h2 className="text-xl font-semibold mb-2">Representation</h2>
          <p className="mb-4">
            In each of the identified groups, the following comments best
            represent the views of that group.
          </p>
          {conversationAnalysis.groups.map((group) => (
            <div key={group.group_id} className="mb-6">
              <h3 className="text-lg font-semibold mb-2">
                Group {group.group_id} (Members: {group.users.length})
              </h3>
              {group.representative_comments.length === 0 && (
                <p>No representative comments for this group.</p>
              )}
              {group.representative_comments.length > 0 && (
                <table className="min-w-full border border-gray-300">
                  <thead>
                    <tr className="bg-gray-200">
                      <th className="border border-gray-300 px-4 py-2 text-left w-1/2">
                        Comment
                      </th>
                      <th className="border border-gray-300 px-4 py-2 text-left w-1/4">
                        Percentage of Group Agreeing
                      </th>
                      <th className="border border-gray-300 px-4 py-2 text-left w-1/4">
                        Representation Score
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {group.representative_comments.map((comment) => (
                      <tr key={comment.id}>
                        <td className="border border-gray-300 px-4 py-2">
                          {comment.content}
                        </td>
                        <td className="border border-gray-300 px-4 py-2">
                          {`${(comment.agree_percentage * 100).toFixed(0)}%`}
                        </td>
                        <td className="border border-gray-300 px-4 py-2">
                          <div className="flex items-center">
                            <div className="relative w-32 h-4 bg-gray-200 rounded">
                              <div
                                className={
                                  "absolute top-0 left-0 h-full rounded bg-blue-500"
                                }
                                style={{
                                  width: `${
                                    (comment.representativeness * 100) / 5
                                  }%`,
                                }}
                              />
                            </div>
                            <span className="ml-2 text-sm">
                              {` (${comment.representativeness.toFixed(2)})`}
                            </span>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          ))}
        </div>
      </section>
    </CoreBase>
  );
}
