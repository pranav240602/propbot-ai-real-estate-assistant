"""
Tests for Airflow DAG orchestration logic
"""
import pytest
from airflow.models import DagBag

class TestDAGValidation:
    """Test DAG validation and structure"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.dagbag = DagBag(dag_folder='dags/', include_examples=False)
    
    def test_dag_loaded(self):
        """Test that DAG is properly loaded without errors"""
        assert 'propbot_data_pipeline' in self.dagbag.dags, "DAG 'propbot_data_pipeline' not found"
        assert len(self.dagbag.import_errors) == 0, f"Import errors: {self.dagbag.import_errors}"
    
    def test_dag_schedule(self):
        """Test DAG scheduling configuration"""
        dag = self.dagbag.get_dag('propbot_data_pipeline')
        assert dag.schedule_interval is not None, "DAG should have a schedule"
        assert dag.catchup == False, "DAG should not catchup"
    
    def test_task_count(self):
        """Test that DAG has expected number of tasks"""
        dag = self.dagbag.get_dag('propbot_data_pipeline')
        assert len(dag.tasks) >= 5, "DAG should have at least 5 tasks"

class TestTaskDependencies:
    """Test task dependencies and execution order"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.dagbag = DagBag(dag_folder='dags/', include_examples=False)
        self.dag = self.dagbag.get_dag('propbot_data_pipeline')
    
    def test_fetch_tasks_exist(self):
        """Test that data fetching tasks exist"""
        task_ids = [task.task_id for task in self.dag.tasks]
        fetch_tasks = [t for t in task_ids if 'fetch' in t.lower()]
        assert len(fetch_tasks) > 0, "Should have data fetching tasks"
    
    def test_preprocessing_tasks_exist(self):
        """Test that preprocessing tasks exist"""
        task_ids = [task.task_id for task in self.dag.tasks]
        preprocess_tasks = [t for t in task_ids if 'preprocess' in t.lower() or 'clean' in t.lower()]
        assert len(preprocess_tasks) > 0, "Should have preprocessing tasks"
    
    def test_validation_task_exists(self):
        """Test that validation task exists"""
        task_ids = [task.task_id for task in self.dag.tasks]
        validation_tasks = [t for t in task_ids if 'validat' in t.lower()]
        assert len(validation_tasks) > 0, "Should have validation tasks"
