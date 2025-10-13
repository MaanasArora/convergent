import { useParams } from 'react-router';
import CoreBase from './base';
import { useQuery } from '@tanstack/react-query';
import { getApi } from '../../components/api/base';
import dayjs from 'dayjs';
import { Conversation } from './dashboard';

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
    queryKey: ['conversation', conversationId],
    queryFn: () => getApi(`/conversations/${conversationId}`),
    enabled: !!conversationId,
  });
  const conversation = conversationResponse.data as Conversation;

  const conversationAnalysisResponse = useQuery({
    queryKey: ['conversation-analysis', conversationId],
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
        <div className='flex justify-center items-center h-64'>
          <div className='text-gray-500'>Loading analysis...</div>
        </div>
      </CoreBase>
    );
  }

  // Get top 5 consensus comments
  const topConsensus = conversationAnalysis.comments_by_consensus.slice(0, 5);

  // Get top 2 representative comments for each group
  const groupRepresentatives = conversationAnalysis.groups.map((group) => ({
    ...group,
    topComments: group.representative_comments
      .sort((a, b) => b.representativeness - a.representativeness)
      .slice(0, 2),
  }));

  return (
    <CoreBase requiresLogin={true}>
      <style>{`
        @media print {
          body, html {
            overflow: visible !important;
            height: auto !important;
          }
          body * {
            overflow: visible !important;
            height: auto !important;
            max-height: none !important;
          }
        }
      `}</style>
      <div className='max-w-6xl mx-auto bg-white'>
        {/* Header */}
        <div className='bg-gray-700 text-white px-16 py-12 border-b-4 border-gray-600'>
          <h1 className='text-4xl font-semibold mb-4'>{conversation.name}</h1>
          <p className='text-lg opacity-90 mb-8'>{conversation.description}</p>
          <div className='flex gap-10 text-sm opacity-85'>
            <div>
              {dayjs(conversation.date_created).format('MMMM D, YYYY')}
            </div>
            <div>{conversation.author.username}</div>
          </div>
        </div>

        {/* Stats Bar */}
        <div className='grid grid-cols-4 gap-0 border-b-2 border-gray-300 bg-gray-50'>
          <div className='px-8 py-8 text-center border-r border-gray-300'>
            <div className='text-4xl font-semibold text-gray-700 mb-2'>
              {conversationAnalysis.user_ids.length}
            </div>
            <div className='text-sm text-gray-600 uppercase tracking-wide font-medium'>
              Participants
            </div>
          </div>
          <div className='px-8 py-8 text-center border-r border-gray-300'>
            <div className='text-4xl font-semibold text-gray-700 mb-2'>
              {conversationAnalysis.comment_ids.length}
            </div>
            <div className='text-sm text-gray-600 uppercase tracking-wide font-medium'>
              Statements
            </div>
          </div>
          <div className='px-8 py-8 text-center border-r border-gray-300'>
            <div className='text-4xl font-semibold text-gray-700 mb-2'>
              {topConsensus.length}
            </div>
            <div className='text-sm text-gray-600 uppercase tracking-wide font-medium'>
              Top Consensus
            </div>
          </div>
          <div className='px-8 py-8 text-center'>
            <div className='text-4xl font-semibold text-gray-700 mb-2'>
              {conversationAnalysis.groups.length}
            </div>
            <div className='text-sm text-gray-600 uppercase tracking-wide font-medium'>
              Opinion Groups
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className='px-16 py-12'>
          {/* Opinion Groups */}
          {conversationAnalysis.groups.length > 0 && (
            <div className='mb-16'>
              <h2 className='text-3xl font-semibold mb-6 text-gray-900 pb-3 border-b-2 border-gray-300'>
                Opinion Landscape
              </h2>
              <div className='bg-gray-50 rounded-lg p-10 border border-gray-300'>
                <p className='text-lg mb-8 text-gray-700'>
                  {conversationAnalysis.groups.length} distinct opinion groups
                  emerged from the conversation
                </p>

                {/* Bar chart of group sizes */}
                <div className='space-y-4 mb-8'>
                  {conversationAnalysis.groups
                    .sort((a, b) => b.users.length - a.users.length)
                    .map((group) => {
                      const maxSize = Math.max(
                        ...conversationAnalysis.groups.map(
                          (g) => g.users.length
                        )
                      );
                      const percentage = (group.users.length / maxSize) * 100;

                      return (
                        <div
                          key={group.group_id}
                          className='flex items-center gap-4'>
                          <div className='w-24 text-sm font-semibold text-gray-700'>
                            Group {group.group_id}
                          </div>
                          <div className='flex-1'>
                            <div className='relative h-10 bg-gray-200 rounded overflow-hidden'>
                              <div
                                className='absolute top-0 left-0 h-full bg-gray-600 rounded flex items-center justify-end pr-3 transition-all duration-500'
                                style={{ width: `${percentage}%` }}>
                                <span className='text-white text-sm font-semibold'>
                                  {group.users.length} participants
                                </span>
                              </div>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                </div>

                <div className='flex gap-8 flex-wrap'>
                  {conversationAnalysis.groups.map((group) => (
                    <div
                      key={group.group_id}
                      className='flex items-center gap-3'>
                      <div className='w-5 h-5 bg-gray-600 rounded border border-gray-400' />
                      <div className='text-gray-700'>
                        <strong>Group {group.group_id}:</strong>{' '}
                        {group.users.length} participants
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Points of Consensus */}
          {topConsensus.length > 0 && (
            <div className='mb-16'>
              <h2 className='text-3xl font-semibold mb-6 text-gray-900 pb-3 border-b-2 border-gray-300'>
                Points of Consensus
              </h2>
              <div className='space-y-3'>
                {topConsensus.map((comment) => (
                  <div
                    key={comment.id}
                    className='bg-gray-50 border border-gray-300 rounded-lg px-5 py-4 flex items-center gap-4'>
                    <div className='flex items-center gap-2 bg-gray-700 text-white px-3 py-1.5 rounded text-xs font-semibold uppercase tracking-wide flex-shrink-0'>
                      <span className='bg-white/20 px-2 py-0.5 rounded'>
                        {comment.consensus.toFixed(2)}
                      </span>
                    </div>
                    <p className='text-base text-gray-900 leading-snug'>
                      "{comment.content}"
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Representative Statements by Group */}
          {conversationAnalysis.groups.length > 0 &&
            groupRepresentatives.some((g) => g.topComments.length > 0) && (
              <div className='mb-16'>
                <h2 className='text-3xl font-semibold mb-6 text-gray-900 pb-3 border-b-2 border-gray-300'>
                  What Each Group Values
                </h2>
                <p className='text-gray-700 mb-8 leading-relaxed'>
                  The following statements best represent what matters most to
                  each opinion group.
                </p>
                {groupRepresentatives.map(
                  (group) =>
                    group.topComments.length > 0 && (
                      <div key={group.group_id} className='mb-8'>
                        <h3 className='text-xl font-semibold mb-4 text-gray-900'>
                          Group {group.group_id} ({group.users.length}{' '}
                          participants)
                        </h3>
                        <div className='space-y-4'>
                          {group.topComments.map((comment) => (
                            <div
                              key={comment.id}
                              className='bg-gray-50 border border-gray-300 rounded-lg p-6'>
                              <p className='text-lg text-gray-900 leading-relaxed mb-3'>
                                "{comment.content}"
                              </p>
                              <div className='flex items-center gap-6 text-sm text-gray-600'>
                                <div>
                                  <strong className='text-gray-900'>
                                    {(comment.agree_percentage * 100).toFixed(
                                      0
                                    )}
                                    %
                                  </strong>{' '}
                                  of group agrees
                                </div>
                                <div>
                                  Representativeness:{' '}
                                  <strong className='text-gray-900'>
                                    {comment.representativeness.toFixed(2)}
                                  </strong>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )
                )}
              </div>
            )}

          {/* Complete Statement Rankings */}
          <div className='mb-16'>
            <h2 className='text-3xl font-semibold mb-6 text-gray-900 pb-3 border-b-2 border-gray-300'>
              Complete Statement Rankings
            </h2>
            <div className='border border-gray-300 rounded-lg overflow-hidden'>
              <table className='w-full'>
                <thead>
                  <tr className='bg-gray-50'>
                    <th className='px-4 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wide border-b-2 border-gray-300 w-16'>
                      #
                    </th>
                    <th className='px-4 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wide border-b-2 border-gray-300'>
                      Statement
                    </th>
                    <th className='px-4 py-4 text-center text-xs font-semibold text-gray-700 uppercase tracking-wide border-b-2 border-gray-300 w-32'>
                      Consensus
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {conversationAnalysis.comments_by_consensus.map(
                    (comment, index) => (
                      <tr
                        key={comment.id}
                        className='hover:bg-gray-50 transition-colors'>
                        <td className='px-4 py-4 border-b border-gray-200 text-gray-600 font-semibold'>
                          {index + 1}
                        </td>
                        <td className='px-4 py-4 border-b border-gray-200 text-gray-900'>
                          {comment.content}
                        </td>
                        <td className='px-4 py-4 border-b border-gray-200 text-center text-lg font-semibold text-gray-700'>
                          {comment.consensus.toFixed(2)}
                        </td>
                      </tr>
                    )
                  )}
                  {conversationAnalysis.comments_by_consensus.length === 0 && (
                    <tr>
                      <td
                        colSpan={3}
                        className='px-4 py-8 text-center text-gray-500'>
                        No statements available for analysis.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* All Representative Comments by Group */}
          {conversationAnalysis.groups.length > 0 && (
            <div className='mb-16'>
              <h2 className='text-3xl font-semibold mb-6 text-gray-900 pb-3 border-b-2 border-gray-300'>
                All Representative Statements by Group
              </h2>
              <p className='text-gray-700 mb-8 leading-relaxed'>
                Complete list of statements that represent each opinion group's
                perspectives.
              </p>
              {conversationAnalysis.groups.map((group) => (
                <div key={group.group_id} className='mb-10'>
                  <h3 className='text-xl font-semibold mb-4 text-gray-900'>
                    Group {group.group_id} ({group.users.length} participants)
                  </h3>
                  {group.representative_comments.length === 0 ? (
                    <p className='text-gray-600 italic'>
                      No representative statements for this group.
                    </p>
                  ) : (
                    <div className='border border-gray-300 rounded-lg overflow-hidden'>
                      <table className='w-full'>
                        <thead>
                          <tr className='bg-gray-50'>
                            <th className='px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wide border-b-2 border-gray-300'>
                              Statement
                            </th>
                            <th className='px-4 py-3 text-center text-xs font-semibold text-gray-700 uppercase tracking-wide border-b-2 border-gray-300 w-40'>
                              Group Agreement
                            </th>
                            <th className='px-4 py-3 text-center text-xs font-semibold text-gray-700 uppercase tracking-wide border-b-2 border-gray-300 w-40'>
                              Representativeness
                            </th>
                          </tr>
                        </thead>
                        <tbody>
                          {group.representative_comments.map((comment) => (
                            <tr
                              key={comment.id}
                              className='hover:bg-gray-50 transition-colors'>
                              <td className='px-4 py-4 border-b border-gray-200 text-gray-900'>
                                {comment.content}
                              </td>
                              <td className='px-4 py-4 border-b border-gray-200 text-center text-lg font-semibold text-gray-700'>
                                {(comment.agree_percentage * 100).toFixed(0)}%
                              </td>
                              <td className='px-4 py-4 border-b border-gray-200 text-center text-lg font-semibold text-gray-700'>
                                {comment.representativeness.toFixed(2)}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className='bg-gray-50 px-16 py-10 border-t-2 border-gray-300'>
          <p className='text-gray-600 text-sm leading-relaxed mb-3'>
            <strong className='text-gray-900'>About This Report:</strong> This
            report summarizes input gathered through Convergent, a platform for
            large-scale democratic dialogue. Data reflects responses from{' '}
            {conversationAnalysis.user_ids.length} participants who voted on{' '}
            {conversationAnalysis.comment_ids.length} statements.
          </p>
          <p className='text-gray-600 text-sm leading-relaxed'>
            <strong className='text-gray-900'>Consensus Score:</strong> The
            consensus score ranges from 0 to 1, where higher scores indicate
            stronger agreement across all participants. Scores above 0.65 are
            generally considered points of consensus.
          </p>
        </div>
      </div>
    </CoreBase>
  );
}
