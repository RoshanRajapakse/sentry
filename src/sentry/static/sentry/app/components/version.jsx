import PropTypes from 'prop-types';
import React from 'react';

import GlobalSelectionLink from 'app/components/globalSelectionLink';
import Link from 'app/components/links/link';
import withOrganization from 'app/utils/withOrganization';

class Version extends React.Component {
  static propTypes = {
    anchor: PropTypes.bool,
    version: PropTypes.string.isRequired,
    orgId: PropTypes.string,

    /**
     * Should link to Release preserve user's global selection values
     */
    preserveGlobalSelection: PropTypes.bool,
  };

  static defaultProps = {
    anchor: true,
  };

  render() {
    const {orgId, version, anchor, className, preserveGlobalSelection} = this.props;

    const LinkComponent = preserveGlobalSelection ? GlobalSelectionLink : Link;

    if (anchor && orgId) {
      return (
        <LinkComponent
          to={`/organizations/${orgId}/releases/${encodeURIComponent(version)}/`}
          className={className}
        >
          <span title={version}>{version}</span>
        </LinkComponent>
      );
    }

    return (
      <span title={version} className={className}>
        {version}
      </span>
    );
  }
}

export default withOrganization(Version);
