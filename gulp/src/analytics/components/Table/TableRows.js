import React from 'react';
import {Component} from 'react';
import {connect} from 'react-redux';
import {doGetSelectedFilterData} from '../../actions/table-filter-actions';
import NoResults from 'common/ui/NoResults';
import {isEmpty} from 'lodash-compat/lang';

class TableRows extends Component {
  constructor(props) {
    super(props);
  }
  applyFilterResults(tableValue, typeValue) {
    const {dispatch} = this.props;
    dispatch(doGetSelectedFilterData(tableValue, typeValue));
  }
  render() {
    const {rowData, tableData} = this.props;
    const columnData = tableData.PageLoadData.column_names;
    const originalHeader = [];
    const modHeader = [];
    // Looping through the current data and pushing it to a new array to edit it
    columnData.map((colData) => {
      originalHeader.push(colData);
      modHeader.push(colData);
    });
    originalHeader.shift();
    const mod = modHeader.slice(0, 1);
    const getHeaders = rowData.map((item, i) => {
      const firstCell = mod.map((colData, index) => {
        if (isEmpty(tableData.PageLoadData.remaining_dimensions)) {
          return (
            <td key={index} className="last-filter">{item[colData.key]}</td>
          );
        }
        return (
          <td key={index}><a onClick={this.applyFilterResults.bind(this, item[colData.key], colData.key)} href="#">{item[colData.key]}</a></td>
        );
      });
      const cell = originalHeader.map((colData, ind) => {
        return (
          <td key={ind}>{item[colData.key]}</td>
        );
      });

      return <tr key={i}>{firstCell}{cell}</tr>;
    });
    return (
      <tbody>
        {isEmpty(rowData) ? <NoResults type="table" errorMessage="No results found"/> : getHeaders}
      </tbody>
    );
  }
}

TableRows.propTypes = {
  rowData: React.PropTypes.array.isRequired,
  tableData: React.PropTypes.object.isRequired,
  dispatch: React.PropTypes.func.isRequired,
};

export default connect(state => ({
  analytics: state.pageLoadData,
}))(TableRows);
