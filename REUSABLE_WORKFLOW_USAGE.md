# Using the Reusable Accept Image Workflow

The `accept-image-reusable.yml` workflow allows external repositories to programmatically accept new golden images.

## Basic Usage

```yaml
name: Accept Visual Changes
on:
  # Your trigger conditions (e.g., workflow_dispatch, issue comments, etc.)
  
jobs:
  accept-new-image:
    uses: mpiispanen/image-comparison-and-update/.github/workflows/accept-image-reusable.yml@main
    with:
      image: "homepage.png"                    # The image filename to accept
      pr_number: 123                          # PR number in your repository
      target_repo: "your-org/your-repo"       # Your repository (owner/repo format)
      artifact_name: "visual-test-results"    # Name of artifact containing the image
      reference_dir: "golden"                 # Directory to store golden images (optional, defaults to "golden")
    permissions:
      contents: write
      issues: write  
      pull-requests: write
      actions: read
```

## Advanced Example

```yaml
name: Automated Visual Regression Acceptance
on:
  issue_comment:
    types: [created]

jobs:
  parse-accept-command:
    if: github.event.issue.pull_request && startsWith(github.event.comment.body, '/auto-accept')
    runs-on: ubuntu-latest
    outputs:
      should_accept: ${{ steps.check.outputs.should_accept }}
      image_list: ${{ steps.check.outputs.image_list }}
    steps:
      - name: Parse acceptance criteria
        id: check
        run: |
          # Your logic to determine if automatic acceptance should proceed
          # and which images to accept
          echo "should_accept=true" >> $GITHUB_OUTPUT
          echo "image_list=homepage.png,dashboard.png" >> $GITHUB_OUTPUT

  accept-images:
    needs: parse-accept-command
    if: needs.parse-accept-command.outputs.should_accept == 'true'
    strategy:
      matrix:
        image: ${{ fromJson(format('["{0}"]', join(split(needs.parse-accept-command.outputs.image_list, ','), '","'))) }}
    uses: mpiispanen/image-comparison-and-update/.github/workflows/accept-image-reusable.yml@main
    with:
      image: ${{ matrix.image }}
      pr_number: ${{ github.event.issue.number }}
      target_repo: ${{ github.repository }}
      artifact_name: visual-test-results-${{ github.event.issue.number }}
      reference_dir: assets/golden-images
    permissions:
      contents: write
      issues: write
      pull-requests: write  
      actions: read
```

## Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `image` | string | ✅ Yes | - | The filename to accept (e.g., "homepage.png") |
| `pr_number` | number | ✅ Yes | - | The PR number in the target repository |
| `target_repo` | string | ✅ Yes | - | Repository in "owner/repo" format |
| `artifact_name` | string | ✅ Yes | - | Name of the artifact containing candidate images |
| `reference_dir` | string | ❌ No | "golden" | Directory for storing reference images |

## Security

- Images are validated to ensure they have proper extensions (.png, .jpg, .jpeg)
- Repository names are validated to prevent injection attacks
- The workflow requires write permissions to commit changes
- All operations are logged and attributed

## Error Handling

The workflow will fail and comment on the PR if:
- The specified image is not found in the artifact
- The image file is not a valid image format
- Git operations fail (network issues, permission problems)
- Input validation fails

## Integration with External Systems

This reusable workflow enables integration with:
- Automated testing pipelines that need to accept visual changes
- Code review tools that can trigger acceptance
- Custom scripts that determine when visual changes should be accepted
- Multi-repository visual regression testing systems