import React from 'react';
import {Col, Row} from 'react-bootstrap';

class Overview extends React.Component {
  render() {
    return (
      <Row>
        <Col xs={12}>
          <div className="wrapper-header">
            <h2>Overview</h2>
          </div>
          <div className="product-card no-highlight">
            <p>
              Use this tool to create users and permit them to perform various
              activities.
            </p>
            <p>
              First, create a role. A role is a group of activities (e.g. view
              existing communication records, add new communication records,
              etc.). Then, create a user and assign them to that role. Once
              assigned to a role, that user can execute activities assigned to
              that role.
            </p>
          </div>
        </Col>
      </Row>
    );
  }
}

export default Overview;
