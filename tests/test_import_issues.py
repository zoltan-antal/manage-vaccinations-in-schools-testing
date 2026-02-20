import pytest
from playwright.sync_api import expect

from mavis.test.data import ChildFileMapping
from mavis.test.data.file_mappings import ImportFormatDetails
from mavis.test.data.file_utils import set_first_name_for_child_list
from mavis.test.pages import (
    DashboardPage,
    ImportRecordsWizardPage,
    ImportsPage,
)
from mavis.test.utils import expect_details


@pytest.fixture
def setup_child_import(
    log_in_as_nurse,
    page,
    point_of_care_file_generator,
):
    DashboardPage(page).click_imports()
    ImportsPage(page).click_upload_records()
    ImportRecordsWizardPage(
        page, point_of_care_file_generator
    ).navigate_to_child_record_import()


@pytest.mark.childlist
def test_child_file_upload_close_match(
    setup_child_import,
    page,
    point_of_care_file_generator,
):
    """ """
    ImportRecordsWizardPage(
        page, point_of_care_file_generator
    ).read_and_verify_import_format_details(ImportFormatDetails.CHILD)
    input_file_path, output_file_path = ImportRecordsWizardPage(
        page, point_of_care_file_generator
    ).upload_and_verify_output(ChildFileMapping.RANDOM_CHILD_WITHOUT_NHS_NUMBER)

    file_with_different_first_name = set_first_name_for_child_list(
        input_file_path, "Test"
    )

    ImportRecordsWizardPage(page, point_of_care_file_generator).header.click_mavis_header()
    DashboardPage(page).click_imports()
    ImportsPage(page).click_upload_records()
    ImportRecordsWizardPage(
        page, point_of_care_file_generator
    ).navigate_to_child_record_import()
    ImportRecordsWizardPage(
        page, point_of_care_file_generator
    ).upload_and_verify_output_for_input_output_files(
        file_with_different_first_name, output_file_path
    )

    expect(page.get_by_role("main")).to_contain_text("Close matches to existing records - needs review")
    upload_issues_group = page.get_by_role("group").filter(has_text="1 upload issue")
    upload_issues_group.click()
    expect(upload_issues_group).to_contain_text("Possible match found. Review and confirm.")
    upload_issues_group.get_by_role("link", name="Review").click()

    page.get_by_role("radio", name="Use uploaded child record").click()
    page.get_by_role("button", name="Resolve duplicate").click()

    expect(page.get_by_role("alert", name="Success")).to_contain_text("Record updated")

    print("hello")
