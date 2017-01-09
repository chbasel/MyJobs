import React from 'react';

class Status extends React.Component {
  render() {
    let button = '';
    if (this.props.status === true) {
      button = <span className="label label-success">Active</span>;
    } else if (this.props.status === false) {
      button = <span className="label label-warning">Pending since:<br/>{this.props.lastInvitation}</span>;
    }
    return (
      <span>
        {button}
      </span>
    );
  }
}

Status.propTypes = {
  status: React.PropTypes.bool.isRequired,
  lastInvitation: React.PropTypes.string.isRequired,
};

Status.defaultProps = {
  status: false,
  lastInvitation: false,
};

export default Status;
