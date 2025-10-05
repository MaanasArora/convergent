import { useParams } from 'react-router';
import CoreBase from './base';
import { useQuery } from '@tanstack/react-query';
import { getApi } from '../../components/api/base';

export default function ConversationAnalysisPage() {
  const params = useParams();

  const conversationId = params.conversationId;

  const conversation = useQuery({
    queryKey: ['conversation', conversationId],
    queryFn: () => getApi(`/conversations/${conversationId}`),
    enabled: !!conversationId,
  });

  const conversationAnalysis = useQuery({
    queryKey: ['conversation-analysis', conversationId],
    queryFn: () => getApi(`/analysis/conversation/${conversationId}`),
    enabled: !!conversationId,
  });

  return (
    <CoreBase requiresLogin={true}>
      <section className='xl:w-[90%] w-full mx-auto p-5'>
        <h1 className='text-3xl font-bold mb-4'>
          Analysis: {conversation.data?.name}
        </h1>
      </section>
    </CoreBase>
  );
}
