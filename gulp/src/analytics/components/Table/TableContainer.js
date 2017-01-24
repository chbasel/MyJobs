import React from 'react';
import {Component} from 'react';
import Table from './Table';
import TableColumns from './TableColumns';
import TableRows from './TableRows';


class TableContainer extends Component {
  render() {
    const {tableData} = this.props;
    return (
      <div>
        <Table tableData={tableData}>
          <TableColumns columnData={tableData}/>
          <TableRows rowData={tableData} />
        </Table>
      </div>
    );
  }
}

TableContainer.propTypes = {
  tableData: React.PropTypes.object.isRequired,
};

export default TableContainer;
