import React from 'react';
import {Component} from 'react';
import PageSize from './PageSize';

class Table extends Component {
  constructor() {
    super();
  }

 //  getPage() {
 //    const {tableData, pageSize} = this.props;
 //    const paginationData = tableData.PageLoadData.rows;
 //    const start = pageSize * (this.state.currentPage - 1);
 //    const end = start + pageSize;
 //    return {
 //      currentPage: this.state.currentPage,
 //      data: paginationData.slice(start, end),
 //      numPages: this.getNumPages(),
 //      handleClick: (pageNum) => {return this.handlePageChange(pageNum)},
 //    };
 // }
 // getNumPages() {
 //   const {tableData, pageSize} = this.props;
 //   const paginationData = tableData.PageLoadData.rows;
 //   let numPages = Math.floor(paginationData.length / pageSize);
 //   if (paginationData.length % pageSize > 0) {
 //     numPages++
 //   }
 //   return numPages;
 // }
 // handlePageChange(pageNum) {
 //   this.setState({
 //     currentPage: pageNum
 //   });
 // }
 // pager() {
 //   const {tableData, pageSize} = this.props;
 //   const paginationData = tableData.PageLoadData.rows;
 //   const start = pageSize * (this.state.currentPage - 1);
 //   const end = start + pageSize;
 //   const currentPage = this.state.currentPage;
 //   const data = paginationData.slice(start, end);
 //   const numPages = this.getNumPages();
 //   const handleClick = (pageNum) => {return this.handlePageChange.bind(this, pageNum)};
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
  render() {
    const {tableData, handlePageSizeChange, pageSize, enablePaging} = this.props;
    const count = [1, 2, 3, 4, 5];
    return (
      <div id={'table_data_tab_' + tableData.navId} className="table-data">
        <div id={'table_search_tab_' + tableData.navId} className="table-search">
            </div>
            <div className="clearfix"></div>
        <table id={'data_table_tab_' + tableData.navId} className="title-data rwd-table">
          {this.props.children}
        </table>
        <div className="pagination-container">
          {enablePaging}
          <PageSize showCount={count} handlePageSizeChange={handlePageSizeChange} pageSize={pageSize} />
        </div>
      </div>
    );
  }
}

Table.propTypes = {
  children: React.PropTypes.arrayOf(
    React.PropTypes.element.isRequired,
  ),
  tableData: React.PropTypes.object.isRequired,
};

export default Table;
