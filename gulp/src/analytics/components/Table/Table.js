import React from 'react';
import {Component} from 'react';
import PageSize from './PageSize';
import Pagination from './Pagination';

class Table extends Component {
  render() {
    const {tableData, handlePageSizeChange, pageSize, currentPage, pageChange, count} = this.props;
    return (
      <div id={'table_data_tab_' + tableData.navId} className="table-data">
        <div id={'table_search_tab_' + tableData.navId} className="table-search">
            </div>
            <div className="clearfix"></div>
        <table id={'data_table_tab_' + tableData.navId} className="title-data rwd-table">
          {this.props.children}
        </table>
        <div className="pagination-container">
          <Pagination tableData={tableData} pageSize={pageSize} currentPage={currentPage} pageChange={pageChange} />
          <PageSize showCount={count} handlePageSizeChange={handlePageSizeChange} />
        </div>
        <div className="clearfix"></div>
      </div>
    );
  }
}

Table.propTypes = {
  /**
   * Children for the table including the headers and rows
   */
  children: React.PropTypes.arrayOf(
    React.PropTypes.element.isRequired,
  ),
  /**
   * Data that is supplied to the table
   */
  tableData: React.PropTypes.object.isRequired,
  /**
   * Function supplied in order to change the amount of data shown per page on the page size component
   */
  handlePageSizeChange: React.PropTypes.func,
  /**
   * Page size is a number describing how much data is initially shown on the table
   */
  pageSize: React.PropTypes.number.isRequired,
  /**
   * Current page is a number that shows which page of the pagination is initially shown when the table renders
   */
  currentPage: React.PropTypes.number.isRequired,
  /**
   * Page Change is a function supplied to change the page when using the pagination
   */
  pageChange: React.PropTypes.func.isRequired,
  /**
   * React array of numbers supplied to the page size in order to change the amount of data being shown in the table
   */
  count: React.PropTypes.array,
};

export default Table;
