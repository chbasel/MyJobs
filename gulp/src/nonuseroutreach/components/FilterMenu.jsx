import React from 'react';
import {doFilterRecords, updateTermFilterAction, updateWorkflowFilterAction} from '../actions/navigation-actions';
import {connect} from 'react-redux';
import SelectControls from 'common/ui/SelectControls';
import TextField from 'common/ui/TextField';

/* Menu
   Component for filtering the NUO Record table
 */
class FilterMenu extends React.Component {
  async handleTermChange(term) {
    const {dispatch} = this.props;
    await dispatch(updateTermFilterAction(term));
    await dispatch(doFilterRecords());
  }
  async handleWorkflowChange(workflowId) {
    const {dispatch} = this.props;
    await dispatch(updateWorkflowFilterAction(workflowId));
    await dispatch(doFilterRecords());
  }
  render() {
    const {workflowChoices, termFilter, workflowFilter} = this.props;
    return (
        <div style={{paddingBottom: '10px'}}>
          <h2 className="top">Filter</h2>
          Filter by Term
          <TextField
            name="term-filter"
            value={termFilter}
            onChange={v => this.handleTermChange(v.target.value)}/>
          Filter by Workflow State
          <SelectControls
            choices={workflowChoices}
            value={workflowFilter}
            onSelect={(v) => this.handleWorkflowChange(v)} />
        </div>
    );
  }
}

FilterMenu.propTypes = {
  dispatch: React.PropTypes.func.isRequired,
  workflowChoices: React.PropTypes.arrayOf(
    React.PropTypes.object.isRequired,
  ).isRequired,
  termFilter: React.PropTypes.string.isRequired,
  workflowFilter: React.PropTypes.string.isRequired,
};

export default connect(state => ({
  workflowChoices: state.navigation.workflowChoices,
  termFilter: state.navigation.termFilter,
  workflowFilter: state.navigation.workflowFilter,
}))(FilterMenu);
