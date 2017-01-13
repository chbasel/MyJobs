import React from 'react';
import {Component} from 'react';


class Pagination extends Component {
  constructor() {
    super();
  }
  getNumPages() {
    const {tableData, pageSize} = this.props;
    const paginationData = tableData.PageLoadData.rows;
    let numPages = Math.floor(paginationData.length / pageSize);
    if (paginationData.length % pageSize > 0) {
      numPages++;
    }
    return numPages;
  }
  // pager() {
  //   const {currentPage, pageChange} = this.props;
  //   const numPages = this.getNumPages();
  //   const handleClick = (pageNum) => {return pageChange(pageNum)};
  //   const pageLinks = [];
  //   if (currentPage > 1) {
  //      if (currentPage > 2) {
  //        pageLinks.push(<span className="pageLink" onClick={handleClick(1)}>«</span>);
  //        pageLinks.push(' ');
  //      }
  //      pageLinks.push(<span className="pageLink" onClick={handleClick(currentPage - 1)}>‹</span>);
  //      pageLinks.push(' ');
  //    }
  //    pageLinks.push(<span className="currentPage">Page {currentPage} of {numPages}</span>);
  //    if (currentPage < numPages) {
  //      pageLinks.push(' ');
  //      pageLinks.push(<span className="pageLink" onClick={handleClick(currentPage + 1)}>›</span>);
  //      if (currentPage < numPages - 1) {
  //        pageLinks.push(' ');
  //        pageLinks.push(<span className="pageLink" onClick={handleClick(numPages)}>»</span>);
  //      }
  //    }
  //    return <div className="pager">{pageLinks}</div>;
  //  }
  handlePageChange(pageNum) {
    const {pageChange} = this.props;
    return pageChange(pageNum);
  }
  render() {
    const {currentPage, pageChange} = this.props;
    const numPages = this.getNumPages();
    // const handleClick = (pageNum) => {return pageChange(pageNum)};
    const pageLinks = [];
    if (currentPage > 1) {
       if (currentPage > 2) {
         pageLinks.push(<span className="pageLink" onClick={this.handlePageChange.bind(this, 1)}>«</span>);
         pageLinks.push(' ');
       }
       pageLinks.push(<span className="pageLink" onClick={this.handlePageChange.bind(this, currentPage - 1)}>‹</span>);
       pageLinks.push(' ');
     }
     pageLinks.push(<span className="currentPage">Page {currentPage} of {numPages}</span>);
     if (currentPage < numPages) {
       pageLinks.push(' ');
       pageLinks.push(<span className="pageLink" onClick={this.handlePageChange.bind(this, currentPage + 1)}>›</span>);
       if (currentPage < numPages - 1) {
         pageLinks.push(' ');
         pageLinks.push(<span className="pageLink" onClick={this.handlePageChange.bind(this, numPages)}>»</span>);
       }
     }
    return (
      <div className="pager">{pageLinks}</div>
    );
  }
}

export default Pagination;
