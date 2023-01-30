import {Fragment, useState} from 'react';
import styled from '@emotion/styled';

import AttachmentUrl from 'sentry/components/events/attachmentUrl';
import ImageViewer from 'sentry/components/events/attachmentViewers/imageViewer';
import JsonViewer from 'sentry/components/events/attachmentViewers/jsonViewer';
import LogFileViewer from 'sentry/components/events/attachmentViewers/logFileViewer';
import RRWebJsonViewer from 'sentry/components/events/attachmentViewers/rrwebJsonViewer';
import EventAttachmentActions from 'sentry/components/events/eventAttachmentActions';
import {EventDataSection} from 'sentry/components/events/eventDataSection';
import FileSize from 'sentry/components/fileSize';
import {PanelTable} from 'sentry/components/panels';
import {t} from 'sentry/locale';
import {IssueAttachment} from 'sentry/types';
import {Event} from 'sentry/types/event';
import {useLocation} from 'sentry/utils/useLocation';
import useOrganization from 'sentry/utils/useOrganization';

import EventAttachmentsCrashReportsNotice from './eventAttachmentsCrashReportsNotice';

type EventAttachmentsProps = {
  attachments: IssueAttachment[];
  event: Event;
  onDeleteAttachment: (attachmentId: IssueAttachment['id']) => void;
  projectSlug: string;
};

type AttachmentPreviewOpenMap = Record<string, boolean>;

interface InlineAttachmentsProps
  extends Pick<EventAttachmentsProps, 'event' | 'projectSlug'> {
  attachment: IssueAttachment;
  attachmentPreviews: AttachmentPreviewOpenMap;
}

const getInlineAttachmentRenderer = (attachment: IssueAttachment) => {
  switch (attachment.mimetype) {
    case 'text/plain':
      return attachment.size > 0 ? LogFileViewer : undefined;
    case 'text/json':
    case 'text/x-json':
    case 'application/json':
      if (attachment.name === 'rrweb.json' || attachment.name.startsWith('rrweb-')) {
        return RRWebJsonViewer;
      }
      return JsonViewer;
    case 'image/jpeg':
    case 'image/png':
    case 'image/gif':
      return ImageViewer;
    default:
      return undefined;
  }
};

const hasInlineAttachmentRenderer = (attachment: IssueAttachment): boolean => {
  return !!getInlineAttachmentRenderer(attachment);
};

const attachmentPreviewIsOpen = (
  attachmentPreviews: Record<string, boolean>,
  attachment: IssueAttachment
) => {
  return attachmentPreviews[attachment.id] === true;
};

const InlineEventAttachment = ({
  attachmentPreviews,
  attachment,
  projectSlug,
  event,
}: InlineAttachmentsProps) => {
  const organization = useOrganization();
  const AttachmentComponent = getInlineAttachmentRenderer(attachment);

  if (!AttachmentComponent || !attachmentPreviewIsOpen(attachmentPreviews, attachment)) {
    return null;
  }

  return (
    <AttachmentPreviewWrapper>
      <AttachmentComponent
        orgId={organization.slug}
        projectSlug={projectSlug}
        eventId={event.id}
        attachment={attachment}
      />
    </AttachmentPreviewWrapper>
  );
};

export const EventAttachments = ({
  attachments,
  event,
  onDeleteAttachment,
  projectSlug,
}: EventAttachmentsProps) => {
  const organization = useOrganization();
  const location = useLocation();
  const [attachmentPreviews, setAttachmentPreviews] = useState<AttachmentPreviewOpenMap>(
    {}
  );
  const crashFileStripped = event.metadata.stripped_crash;

  if (!attachments.length && !crashFileStripped) {
    return null;
  }

  const title = t('Attachments (%s)', attachments.length);

  const lastAttachment = attachments.at(-1);
  const lastAttachmentPreviewed =
    lastAttachment && attachmentPreviewIsOpen(attachmentPreviews, lastAttachment);

  const togglePreview = (attachment: IssueAttachment) => {
    setAttachmentPreviews(previewsMap => ({
      ...previewsMap,
      [attachment.id]: !previewsMap[attachment.id],
    }));
  };

  return (
    <EventDataSection type="attachments" title={title}>
      {crashFileStripped && (
        <EventAttachmentsCrashReportsNotice
          orgSlug={organization.slug}
          projectSlug={projectSlug}
          groupId={event.groupID!}
          location={location}
        />
      )}

      {attachments.length > 0 && (
        <StyledPanelTable
          headers={[
            <Name key="name">{t('File Name')}</Name>,
            <Size key="size">{t('Size')}</Size>,
            t('Actions'),
          ]}
        >
          {attachments.map(attachment => (
            <Fragment key={attachment.id}>
              <Name>{attachment.name}</Name>
              <Size>
                <FileSize bytes={attachment.size} />
              </Size>
              <AttachmentUrl
                projectSlug={projectSlug}
                eventId={event.id}
                attachment={attachment}
              >
                {url => (
                  <div>
                    <EventAttachmentActions
                      url={url}
                      onDelete={onDeleteAttachment}
                      onPreview={_attachmentId => togglePreview(attachment)}
                      withPreviewButton
                      previewIsOpen={attachmentPreviewIsOpen(
                        attachmentPreviews,
                        attachment
                      )}
                      hasPreview={hasInlineAttachmentRenderer(attachment)}
                      attachmentId={attachment.id}
                    />
                  </div>
                )}
              </AttachmentUrl>
              <InlineEventAttachment
                {...{attachment, attachmentPreviews, event, projectSlug}}
              />
              {/* XXX: hack to deal with table grid borders */}
              {lastAttachmentPreviewed && (
                <Fragment>
                  <div style={{display: 'none'}} />
                  <div style={{display: 'none'}} />
                </Fragment>
              )}
            </Fragment>
          ))}
        </StyledPanelTable>
      )}
    </EventDataSection>
  );
};

const StyledPanelTable = styled(PanelTable)`
  grid-template-columns: 1fr auto auto;
`;

const Name = styled('div')`
  ${p => p.theme.overflowEllipsis};
`;

const Size = styled('div')`
  text-align: right;
`;

const AttachmentPreviewWrapper = styled('div')`
  grid-column: auto / span 3;
  border: none;
  padding: 0;
`;
