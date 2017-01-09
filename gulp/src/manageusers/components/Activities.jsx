import React from 'react';
import {Col, Row, Table} from 'react-bootstrap';

import {connect} from 'react-redux';

class Activities extends React.Component {
  render() {
    const {activities} = this.props;
    return (
      <Row>
        <Col xs={12}>
          <div className="wrapper-header">
            <h2>Activities</h2>
          </div>
          <div className="product-card-full no-highlight">
            <div className="activities-wrapper">
              {Object.keys(activities).map(app =>
                <span key={app}>
                  <h3>{app}</h3>
                  <Table className="table-activities" striped>
                    <thead>
                      <tr>
                        <th>Activity</th>
                        <th>Description</th>
                      </tr>
                    </thead>
                    <tbody>
                      {activities[app].map(activity =>
                        <tr key={activity.id}>
                          <td>{activity.name}</td>
                          <td>{activity.name}</td>
                        </tr>
                      )}
                    </tbody>
                  </Table>
                </span>
              )}
            </div>
          </div>
        </Col>
      </Row>
    );
  }
}

Activities.propTypes = {
  activities: React.PropTypes.object,
};

export default connect(state => ({
  activities: state.activities,
}))(Activities);
