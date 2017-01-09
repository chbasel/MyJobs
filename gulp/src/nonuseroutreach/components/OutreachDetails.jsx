import React, {PropTypes, Component} from 'react';
import {connect} from 'react-redux';
import OutreachCardContainer from 'nonuseroutreach/components/OutreachCardContainer';

class OutreachDetails extends Component {
  render() {
    const {outreachBody, dateAdded, outreachFrom, outreachSubject, outreachTo, outreachCC} = this.props;
    return (
      <div>
      <OutreachCardContainer />
      <div className="sidebar">
        <h2 className="top">Communication Details</h2>

        <div style={{overflowWrap: 'break-word', wordWrap: 'break-word'}}>
          <div>Date Received: {dateAdded}</div>
          <div>From: {outreachFrom}</div>
          <div>To: {outreachTo}</div>
          <div>CC: {outreachCC}</div>
          <div>Subject: {outreachSubject}</div>
          <div>Body: {outreachBody}</div>
        </div>
      </div>
      </div>
    );
  }
}

OutreachDetails.propTypes = {
  dateAdded: PropTypes.string.isRequired,
  outreachBody: PropTypes.string.isRequired,
  outreachFrom: PropTypes.string.isRequired,
  outreachSubject: PropTypes.string.isRequired,
  outreachTo: PropTypes.string.isRequired,
  outreachCC: PropTypes.string.isRequired,
};

export default connect(state => ({
  dateAdded: state.process.outreach.dateAdded,
  outreachBody: state.process.outreach.outreachBody,
  outreachFrom: state.process.outreach.outreachFrom,
  outreachSubject: state.process.outreach.outreachSubject,
  outreachTo: state.process.outreach.outreachTo,
  outreachCC: state.process.outreach.outreachCC,
}))(OutreachDetails);
