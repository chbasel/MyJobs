import React from 'react';
import {Component} from 'react';
import PageSize from './PageSize';

class Pagination extends Component {
  constructor() {
    super();

    this.state = {
      active: 1,
    };
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
  handlePageChange(pageNum) {
    const {pageChange} = this.props;
    this.setState({
      active: pageNum,
    });
    return pageChange(pageNum);
  }
  render() {
    const {currentPage, showCount, handlePageSizeChange, dataLength} = this.props;
    const start = currentPage - 1;
    const end = start + 5;
    const numPages = this.getNumPages();
    const prevPageLinks = [];
    const pageLinks = [];
    const nextPageLinks = [];
    if (currentPage > 1) {
      if (currentPage > 2) {
        prevPageLinks.push(<button className="page-link beginning-link" onClick={this.handlePageChange.bind(this, 1)}>«</button>);
        prevPageLinks.push(' ');
      }
      prevPageLinks.push(<button className="page-link previous-link" onClick={this.handlePageChange.bind(this, currentPage - 1)}>Prev</button>);
      prevPageLinks.push(' ');
    }
    for (let i = 1; i <= numPages; i++) {
      const page = i;
      pageLinks.push(<button onClick={this.handlePageChange.bind(this, page)} className={this.state.active === page ? 'page-link individual-page active-page' : 'page-link individual-page'}>{page}</button>);
    }
    if (currentPage < numPages) {
      nextPageLinks.push(' ');
      nextPageLinks.push(<button className="page-link next-link" onClick={this.handlePageChange.bind(this, currentPage + 1)}>Next</button>);
      if (currentPage < numPages - 1) {
        nextPageLinks.push(' ');
        nextPageLinks.push(<button className="page-link end-link" onClick={this.handlePageChange.bind(this, numPages)}>»</button>);
      }
    }
    const pages = numPages > 5 ? pageLinks.slice(start, end) : pageLinks;
    return (
      <div className={dataLength > 10 ? 'pager active-pager' : 'pager hide-pager'}>
        <PageSize handlePageChange={this.handlePageChange.bind(this)} currentPage={currentPage} showCount={showCount} handlePageSizeChange={handlePageSizeChange} />
        <div className="page-links-container">
          {prevPageLinks}
          {pages}
          {nextPageLinks}
        </div>
        <div className="clearfix"></div>
      </div>
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
  /**
   * React array of numbers supplied to the page size in order to change the amount of data being shown in the table
   */
  showCount: React.PropTypes.array,
  /**
   * Function supplied in order to change the amount of data shown per page on the page size component
   */
  handlePageSizeChange: React.PropTypes.func,
  /**
   * Length of the data in deciding whether or not to show the pagination
   */
  dataLength: React.PropTypes.number,
};

export default Pagination;
