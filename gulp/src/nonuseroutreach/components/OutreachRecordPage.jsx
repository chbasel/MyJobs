import React from 'react';
import {connect} from 'react-redux';
import {Col, Row} from 'react-bootstrap';
import OutreachRecordTable from './OutreachRecordTable';

/* OutreachRecordPage
 * Component which encapsulates the OutreachRecordTable.
 * Note: While we currently only display a table here, it is intended that this
 * interface will grow to be something more elaborate - Edwin, 6/17/2016
 */
class OutreachRecordPage extends React.Component {
  render() {
    const {records, filteredRecords, filtersActive} = this.props;
    return (
      <Row>
        <Col xs={12}>
          <OutreachRecordTable records={records}
                               filteredRecords={filteredRecords}
                               filtersActive={filtersActive} />
        </Col>
      </Row>
    );
  }
}

OutreachRecordPage.propTypes = {
  dispatch: React.PropTypes.func.isRequired,
  // records are of the shape documented in OutreachRecordTable
  records: React.PropTypes.arrayOf(
    React.PropTypes.object.isRequired,
  ).isRequired,
  filteredRecords: React.PropTypes.arrayOf(
    React.PropTypes.object.isRequired,
  ),
  filtersActive: React.PropTypes.bool.isRequired,
};

export default connect(state => ({
  records: state.records,
  filteredRecords: state.navigation.filteredRecords,
  filtersActive: state.navigation.filtersActive,
}))(OutreachRecordPage);
