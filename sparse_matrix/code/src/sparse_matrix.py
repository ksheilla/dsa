class SparseMatrix:
    def __init__(self, file_path=None, num_rows=None, num_cols=None):
        self.data = {}  # {row: {col: value}}
        self.num_rows = num_rows
        self.num_cols = num_cols

        if file_path:
            self._load_from_file(file_path)

    def _load_from_file(self, file_path):
        try:
            with open(file_path, 'r') as f:
                lines = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")

        if len(lines) < 2:
            raise ValueError("Input file has wrong format")

        rows_line = lines[0].replace(" ", "")
        cols_line = lines[1].replace(" ", "")

        if not rows_line.startswith("rows=") or not cols_line.startswith("cols="):
            raise ValueError("Input file has wrong format")
        
        try:
            self.num_rows = int(rows_line[5:])
            self.num_cols = int(cols_line[5:])
        except ValueError:
            raise ValueError("Input file has wrong format")

        if self.num_rows <= 0 or self.num_cols <= 0:
            raise ValueError("Invalid number of rows or columns")

        for line in lines[2:]:
            cleaned = line.replace(" ", "")
            if not (cleaned.startswith('(') and cleaned.endswith(')')):
                raise ValueError("Input file has wrong format")
            content = cleaned[1:-1]
            parts = content.split(',')
            if len(parts) != 3:
                raise ValueError("Input file has wrong format")

            for part in parts:
                if not self._is_integer(part):
                    raise ValueError("Input file has wrong format")

            row, col, val = map(int, parts)

            if not (0 <= row < self.num_rows and 0 <= col < self.num_cols):
                raise ValueError("Invalid row/column index in input")

            if val == 0:
                continue

            if row not in self.data:
                self.data[row] = {}
            self.data[row][col] = val

    def get_element(self, row, col):
        if row in self.data and col in self.data[row]:
            return self.data[row][col]
        return 0

    def set_element(self, row, col, value):
        if not (0 <= row < self.num_rows and 0 <= col < self.num_cols):
            return

        if value == 0:
            if row in self.data and col in self.data[row]:
                del self.data[row][col]
                if not self.data[row]:  # Remove empty row dict
                    del self.data[row]
            return

        if row not in self.data:
            self.data[row] = {}
        self.data[row][col] = value

    def add(self, other):
        if self.num_rows != other.num_rows or self.num_cols != other.num_cols:
            raise ValueError("Matrices must have same dimensions for addition.")

        result = SparseMatrix(num_rows=self.num_rows, num_cols=self.num_cols)

        all_rows = set(self.data.keys()).union(other.data.keys())
        for row in all_rows:
            all_cols = set()
            if row in self.data:
                all_cols.update(self.data[row].keys())
            if row in other.data:
                all_cols.update(other.data[row].keys())

            for col in all_cols:
                val = self.get_element(row, col) + other.get_element(row, col)
                result.set_element(row, col, val)

        return result

    def subtract(self, other):
        if self.num_rows != other.num_rows or self.num_cols != other.num_cols:
            raise ValueError("Matrices must have same dimensions for subtraction.")

        result = SparseMatrix(num_rows=self.num_rows, num_cols=self.num_cols)

        all_rows = set(self.data.keys()).union(other.data.keys())
        for row in all_rows:
            all_cols = set()
            if row in self.data:
                all_cols.update(self.data[row].keys())
            if row in other.data:
                all_cols.update(other.data[row].keys())

            for col in all_cols:
                val = self.get_element(row, col) - other.get_element(row, col)
                result.set_element(row, col, val)

        return result

    def multiply(self, other):
        if self.num_cols != other.num_rows:
            raise ValueError("Incompatible dimensions for multiplication.")

        result = SparseMatrix(num_rows=self.num_rows, num_cols=other.num_cols)

        for a_row in self.data:
            for a_col in self.data[a_row]:
                a_val = self.get_element(a_row, a_col)

                if a_col not in other.data:
                    continue

                for b_col in other.data[a_col]:
                    b_val = other.get_element(a_col, b_col)
                    product = a_val * b_val

                    current = result.get_element(a_row, b_col)
                    result.set_element(a_row, b_col, current + product)

        return result

    def print_matrix(self):
        print(f"rows={self.num_rows}")
        print(f"cols={self.num_cols}")
        for row in sorted(self.data.keys()):
            for col in sorted(self.data[row].keys()):
                print(f"({row}, {col}, {self.get_element(row, col)})")

    @staticmethod
    def _is_integer(s):
        if not s:
            return False
        if s[0] in '+-':
            s = s[1:]
        return s.isdigit()


# === Main Program for CLI Interaction ===
def main():
    print("Select operation:\n1. add\n2. subtract\n3. multiply")
    operation = input("Enter operation: ").strip()

    path_a = input("Enter path for matrix A: ").strip()
    path_b = input("Enter path for matrix B: ").strip()

    try:
        A = SparseMatrix(path_a)
        B = SparseMatrix(path_b)
    except Exception as e:
        print(f"Error loading matrices: {e}")
        return

    try:
        if operation == "add":
            result = A.add(B)
        elif operation == "subtract":
            result = A.subtract(B)
        elif operation == "multiply":
            result = A.multiply(B)
        else:
            print("Invalid operation selected.")
            return
    except Exception as e:
        print(f"Operation error: {e}")
        return

    print("\nResultant Matrix:")
    result.print_matrix()


if __name__ == "__main__":
    main()
