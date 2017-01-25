import React from 'react';
import {Component} from 'react';
import Table from './Table';
import TableColumns from './TableColumns';
import TableRows from './TableRows';


class TableContainer extends Component {
  constructor() {
    super();

    this.state = {
      pageSize: 10,
      currentPage: 1,
    };

    this.handlePageSizeChange = this.handlePageSizeChange.bind(this);
    this.handlePageChange = this.handlePageChange.bind(this);
  }
  componentWillReceiveProps() {
    this.setState({
      currentPage: 1,
    });
  }
  handlePageChange(pageNum) {
    this.setState({
      currentPage: pageNum,
    });
  }
  handlePageSizeChange(e) {
    const {tableData} = this.props;
    const rowData = tableData.PageLoadData.rows;
    const size = e.target.value === 'All' ? Number(rowData.length) : Number(e.target.value);
    this.setState({
      pageSize: size,
    });
  }
  render() {
    const {tableData} = this.props;
    const pageSize = this.state.pageSize;
    const currentPage = this.state.currentPage;
    const rowData = tableData.PageLoadData.rows;
    const start = pageSize * (currentPage - 1);
    const end = start + pageSize;
    const paginationData = rowData.slice(start, end);
    const count = [10, 15, 20, 25, 'All'];
    return (
      <div>
        <Table dataLength={rowData.length}count={count} pageChange={this.handlePageChange} currentPage={this.state.currentPage} handlePageSizeChange={this.handlePageSizeChange} pageSize={this.state.pageSize} tableData={tableData}>
          <TableColumns columnData={tableData}/>
          <TableRows pageSize={this.state.pageSize} rowData={paginationData} tableData={tableData} />
        </Table>
      </div>
    );
  }
}

TableContainer.propTypes = {
  tableData: React.PropTypes.object.isRequired,
};

export default TableContainer;
