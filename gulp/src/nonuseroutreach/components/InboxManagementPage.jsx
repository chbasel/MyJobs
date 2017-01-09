import React from 'react';
import {connect} from 'react-redux';
import Inbox from './Inbox';
import {Col, Row} from 'react-bootstrap';

/* InboxManagementPage
 * Component which allows the user to configure new and existing outreach
 * inboxes.
 */
class InboxManagementPage extends React.Component {
  render() {
    const {dispatch, inboxes} = this.props;

    return (
      <div className="cardWrapper">
        <Row>
          <Col xs={12}>
            <div className="wrapper-header">
              <h2>Non-User Outreach Inboxes</h2>
            </div>
            {inboxes.map(inbox =>
              <div
                key={'inbox-' + inbox.pk}
                className="product-card no-highlight clearfix">
                <Row>
                  <Col xs={12}>
                    <Inbox dispatch={dispatch} inbox={inbox} />
                  </Col>
                </Row>
              </div>
            )}
          </Col>
        </Row>
      </div>
    );
  }
}

InboxManagementPage.propTypes = {
  dispatch: React.PropTypes.func.isRequired,
  // inboxes are of the shape documented in Inbox.propTypes
  inboxes: React.PropTypes.arrayOf(
    React.PropTypes.object.isRequired,
  ),
};

export default connect(state => ({
  inboxes: state.inboxes,
}))(InboxManagementPage);
