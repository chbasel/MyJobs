import React, {Component, PropTypes} from 'react';

import {HelpText} from './HelpText';
import {EmailInput} from './EmailInput';
import {ControlButtons} from './ControlButtons';


/**
 * Contain dynamic email editing states
 *
 * type is text of button function identifier
 * disabled is whether the button is disabled or not
 *
 * by default, it is not disabled
 */
class ControlButton {
  constructor(type, disabled, primary, callback) {
    this.type = type;
    this.disabled = disabled;
    this.primary = primary;
    this.callback = callback;
  }
}

/**
 * individual inbox loaded from DB
 *
 * contains inbox textbox and control buttons
 */
export class InboxRow extends Component {
  constructor(props) {
    super(props);
    const {inbox} = props;
    this.state = {
      id: inbox.pk,
      initial_email: inbox.fields.email,
      currentEmail: inbox.fields.email,
      validationMessages: [],
    };
  }

  emailFieldChanged(value) {
    const {inboxManager} = this.props;
    const validationObject = inboxManager.validateEmailInput(value);
    this.setState({
      currentEmail: value,
      success: validationObject.success,
      validationMessages: validationObject.messages,
    });
  }

  deleteEmail() {
    /*
    // Taking out since eslint hates confirm.
    // Need a real modal here.
    const message = 'Are you sure you want to delete ' +
      this.state.initial_email + '@my.jobs?';
    if (!confirm(message)) {
      return;
    }
    */
    this.props.handleDelete(this.props.index);
  }

  saveEmail() {
    this.props.loadInboxesFromApi();
    return;
  }

  cancelChanges() {
    this.setState({
      currentEmail: this.state.initial_email,
      validationMessages: [],
    });
  }

  render() {
    const validationMessages =
      this.state.validationMessages.map((message, i) =>
        <HelpText message={message} key={i} />
      );
    let buttons;
    if (this.state.currentEmail !== this.state.initial_email) {
      buttons = [
        new ControlButton('Save', !this.state.success, true,
          () => this.saveEmail()),
        new ControlButton('Cancel', false, false, () => this.cancelChanges()),
      ];
    } else {
      buttons = [
        new ControlButton('Delete', false, true, () => this.deleteEmail()),
      ];
    }
    return (
      <div className="product-card no-highlight clearfix ">
        {validationMessages}
        <div className="col-xs-12">
          <EmailInput
            id={this.state.id.toString()}
            email={this.state.currentEmail}
            emailFieldChanged={v => this.emailFieldChanged(v)} />
          <ControlButtons
            buttons={buttons}
            buttonClicked={b => b.callback()} />
          </div>
      </div>
    );
  }
}

InboxRow.propTypes = {
  inbox: PropTypes.object.isRequired,
  inboxManager: PropTypes.object.isRequired,
  handleDelete: PropTypes.func.isRequired,
  loadInboxesFromApi: PropTypes.func.isRequired,
  index: PropTypes.number.isRequired,
};
