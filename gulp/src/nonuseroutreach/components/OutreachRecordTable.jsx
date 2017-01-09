import React from 'react';
import {Link} from 'react-router';
import {BootstrapTable, TableHeaderColumn} from 'react-bootstrap-table';

/* OutreachRecordTable
 * Component which displays a list of outreach records (the OutreachRecord model
 * in Django).
 */

export default class OutreachRecordTable extends React.Component {
  reviewFormatter(recordId) {
    return (
      <Link
        className="btn"
        to={`/process?id=${recordId}`}
        >
        Review
      </Link>
    );
  }

  render() {
    const {records, filteredRecords, filtersActive} = this.props;
    const displayData = filtersActive ? filteredRecords : records;
    return (
      <BootstrapTable data={displayData}
                      hover
                      striped
                      bordered={false}
                      height="600px"
                      tableStyle={{marginTop: '0px'}}
                      options={{paginationSize: 3,
                                noDataText: 'No records found'}}>
         <TableHeaderColumn dataField="fromEmail"
                           dataAlign="left"
                           width="225"
                           dataSort>Email
        </TableHeaderColumn>
        <TableHeaderColumn dataField="dateAdded"
                           dataAlign="left"
                           dataSort
                           isKey>Date
        </TableHeaderColumn>
        <TableHeaderColumn dataField="currentWorkflowState"
                           dataAlign="left"
                           dataSort>Status
        </TableHeaderColumn>
        <TableHeaderColumn dataField="id"
                           dataAlign="left"
                           dataFormat={this.reviewFormatter} />
      </BootstrapTable>
    );
  }
}

OutreachRecordTable.propTypes = {
  records: React.PropTypes.arrayOf(
    React.PropTypes.shape({
      // date teh record was created
      dateAdded: React.PropTypes.string.isRequired,
      // the inbox the record went to
      outreachEmail: React.PropTypes.string.isRequired,
      // the email the record was created from
      fromEmail: React.PropTypes.string.isRequired,
      // denotes what action, if any, was taken on the record (pending,
      // unprocessed, etc)
      currentWorkflowState: React.PropTypes.string.isRequired,
    }).isRequired,
  ).isRequired,
  filteredRecords: React.PropTypes.arrayOf(
    React.PropTypes.shape({
      // date teh record was created
      dateAdded: React.PropTypes.string.isRequired,
      // the inbox the record went to
      outreachEmail: React.PropTypes.string.isRequired,
      // the email the record was created from
      fromEmail: React.PropTypes.string.isRequired,
      // denotes what action, if any, was taken on the record (pending,
      // unprocessed, etc)
      currentWorkflowState: React.PropTypes.string.isRequired,
    }).isRequired,
  ).isRequired,
  filtersActive: React.PropTypes.bool.isRequired,
};
