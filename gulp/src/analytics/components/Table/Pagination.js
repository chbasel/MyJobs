import React from 'react';
import {Component} from 'react';

class Pagination extends Component {
  getNumPages() {
    const {tableData, pageSize} = this.props;
    const paginationData = tableData.PageLoadData.rows;
    let numPages = Math.floor(paginationData.length / pageSize);
    if (paginationData.length % pageSize > 0) {
      numPages++;
    }
    return numPages;
  }
  handlePageChange(pageNum) {
    const {pageChange} = this.props;
    return pageChange(pageNum);
  }
  render() {
    const {currentPage} = this.props;
    const numPages = this.getNumPages();
    const pageLinks = [];
    if (currentPage > 1) {
      if (currentPage > 2) {
        pageLinks.push(<span className="page-link beginning-link" onClick={this.handlePageChange.bind(this, 1)}>«</span>);
        pageLinks.push(' ');
      }
      pageLinks.push(<span className="page-link previous-link" onClick={this.handlePageChange.bind(this, currentPage - 1)}>Prev</span>);
      pageLinks.push(' ');
    }
    pageLinks.push(<span className="current-page">Page {currentPage} of {numPages}</span>);
    if (currentPage < numPages) {
      pageLinks.push(' ');
      pageLinks.push(<span className="page-link next-link" onClick={this.handlePageChange.bind(this, currentPage + 1)}>Next</span>);
      if (currentPage < numPages - 1) {
        pageLinks.push(' ');
        pageLinks.push(<span className="page-link end-link" onClick={this.handlePageChange.bind(this, numPages)}>»</span>);
      }
    }
    return (
      <div className="pager">{pageLinks}</div>
    );
  }
}

Pagination.propTypes = {
  /**
   * Data supplied to the table from redux
   */
  tableData: React.PropTypes.object.isRequired,
  /**
   * Number supplied in order to get the current amount of data being shown inside of the table
   */
  pageSize: React.PropTypes.number.isRequired,
  /**
   * Function supplied in order to handle the pagination page changing
   */
  pageChange: React.PropTypes.func.isRequired,
  /**
   * Current page is a number supplied in order to know which page is currently being displayed with data in the table
   */
  currentPage: React.PropTypes.number.isRequired,
};

export default Pagination;
