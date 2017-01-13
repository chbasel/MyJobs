import React from 'react';
import {Component} from 'react';
import Table from './Table';
import TableColumns from './TableColumns';
import TableRows from './TableRows';


class TableContainer extends Component {
  constructor() {
    super();

    this.state = {
      pageSize: 2,
      currentPage: 1,
    };

    this.handlePageSizeChange = this.handlePageSizeChange.bind(this);
    this.pager = this.pager.bind(this);
  }
  componentWillReceiveProps() {
    this.setState({
      currentPage: 1,
    });
  }
  getNumPages() {
    const {tableData} = this.props;
    const pageSize = this.state.pageSize;
    const paginationData = tableData.PageLoadData.rows;
    let numPages = Math.floor(paginationData.length / pageSize);
    if (paginationData.length % pageSize > 0) {
      numPages++
    }
    return numPages;
  }
  handlePageChange(pageNum) {
    this.setState({
      currentPage: pageNum
    });
  }
  handlePageSizeChange(e) {
    this.setState({
      pageSize: Number(e.target.value),
    });
  }
  pager() {
    const currentPage = this.state.currentPage;
    const numPages = this.getNumPages();
    const handleClick = (pageNum) => {return this.handlePageChange(pageNum)};
    const pageLinks = [];
    if (currentPage > 1) {
       if (currentPage > 2) {
         pageLinks.push(<span className="pageLink" onClick={handleClick(1)}>«</span>);
         pageLinks.push(' ');
       }
       pageLinks.push(<span className="pageLink" onClick={handleClick(currentPage - 1)}>‹</span>);
       pageLinks.push(' ');
     }
     pageLinks.push(<span className="currentPage">Page {currentPage} of {numPages}</span>);
     if (currentPage < numPages) {
       pageLinks.push(' ');
       pageLinks.push(<span className="pageLink" onClick={handleClick(currentPage + 1)}>›</span>);
       if (currentPage < numPages - 1) {
         pageLinks.push(' ');
         pageLinks.push(<span className="pageLink" onClick={handleClick(numPages)}>»</span>);
       }
     }
     return <div className="pager">{pageLinks}</div>;
   }
  render() {
    const {tableData} = this.props;
    const pageSize = this.state.pageSize;
    const currentPage = this.state.currentPage;
    const rowData = tableData.PageLoadData.rows;
    const start = pageSize * (currentPage - 1);
    const end = start + pageSize;
    const paginationData = rowData.slice(start, end);
    return (
      <div>
        <Table enablePaging={this.pager} handlePageSizeChange={this.handlePageSizeChange} pageSize={this.state.pageSize} tableData={tableData}>
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
