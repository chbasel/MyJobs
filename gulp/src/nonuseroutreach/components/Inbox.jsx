import React from 'react';
import HelpText from '../../common/ui/HelpText';
import {
  Button,
  ButtonGroup,
  Col,
  FormControl,
  InputGroup,
  Row,
} from 'react-bootstrap';

import {
  validateInboxAction,
  resetInboxAction,
  doUpdateInbox,
  doSaveInbox,
  doDeleteInbox,
} from '../actions/inbox-actions';

import {runConfirmInPlace} from 'common/actions/confirm-actions';

/* Inbox
 * Component for manipulating NonUser Outreach inboxes (the
 * OutreachEmailAddress model in Django)
 */


export default class Inbox extends React.Component {

  async handleDelete() {
    const {dispatch, inbox} = this.props;
    const message = 'Are you sure you want to delete this inbox?';
    if (await runConfirmInPlace(dispatch, message)) {
      dispatch(doDeleteInbox(inbox));
    }
  }

  render() {
    const {dispatch, inbox} = this.props;
    // For new inboxes, we only show the add button. For existing inboxes, we
    // show the delete button, unless the email has changed, in which case we
    // show the Update and Cancel buttons.
    let buttons;
    if (inbox.pk) {
      if (inbox.email === inbox.originalEmail) {
        buttons = [
          <Button
            key={'delete-' + inbox.pk}
            onClick={() => this.handleDelete(inbox)}>
            Delete
          </Button>,
        ];
      } else {
        buttons = [
          <Button
            key={'update-' + inbox.pk}
            disabled={!inbox.valid}
            onClick={() => dispatch(doUpdateInbox(inbox))}>
            Update
          </Button>,
          <Button
            key={'cancel-' + inbox.pk}
            onClick={() => dispatch(resetInboxAction(inbox))}>
            Cancel
          </Button>,
        ];
      }
    } else {
      buttons = [
        <Button
          key={'add-' + inbox.pk}
          disabled={!inbox.valid}
          onClick={() => dispatch(doSaveInbox(inbox))} >
          Add
        </Button>,
      ];
    }

    return (
      <div>
        {inbox.errors.map((error, index) =>
          <HelpText key={index} message={error} />)}
        <Row>
          <Col md={8} xs={12}>
            <InputGroup>
              <FormControl
                type="text"
                className="email-input"
                value={inbox.email}
                ref="email_input"
                autoFocus={!inbox.pk}
                onChange={e => dispatch(validateInboxAction({
                  ...inbox,
                  email: e.target.value,
                }))}/>
              <InputGroup.Addon>@my.jobs</InputGroup.Addon>
            </InputGroup>
          </Col>
          <Col md={4} xs={12}>
            <ButtonGroup className="pull-right">
              {buttons}
            </ButtonGroup>
          </Col>
        </Row>
      </div>
    );
  }
}

Inbox.propTypes = {
  // method used to evoke Redux actions
  dispatch: React.PropTypes.func.isRequired,
  inbox: React.PropTypes.shape({
    // primary key for the inbox; null for new inboxes
    pk: React.PropTypes.number,
    // this is the original email before editing occurred; null for new inboxes
    originalEmail: React.PropTypes.string,
    // the local part of the email address associated with the inbox
    email: React.PropTypes.string.isRequired,
    // any validation errors which occured for the provided email
    errors: React.PropTypes.arrayOf(React.PropTypes.string).isRequired,
    // whether the email is valid; absense of errors does *not* imply validity
    valid: React.PropTypes.bool.isRequired,
  }).isRequired,
};
