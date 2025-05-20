
1. Sinh viên thực hiện: Phan Trọng Ngọc Anh - N21DCCN099

2. Đề bài:
    Viết chương trình thực hiện chỉ mục nghịch đảo với các chức năng chính:
    - CreateIndex(Dir, StopList): Tạo chỉ mục nghịch đảo từ thư mục tài liệu và file stoplist.
    - Find(Word, Weight, N): Tìm top N tài liệu chứa từ Word với trọng số Weight.
    - Find(WordFile, N): Tìm top N tài liệu theo danh sách từ khóa + trọng số trong file WordFile.

3. Mô tả dự án:
    - Ứng dụng sử dụng Python với thư viện Tkinter để xây dựng giao diện người dùng.
    - Tạo chỉ mục nghịch đảo từ thư mục tài liệu, loại bỏ từ trong stoplist.
    - Tìm kiếm tài liệu theo từ khóa đơn hoặc danh sách từ khóa trọng số.
    - Hiển thị kết quả và chỉ mục qua giao diện trực quan.
    - Có xử lý đa luồng khi tạo chỉ mục để không làm đơ giao diện.

4. Hướng dẫn cài đặt:
    - Tải và cài Python 3.x tại https://www.python.org/downloads/windows/
    - Đảm bảo python --version chạy được trên CMD hoặc PowerShell.
    - Không cần pip install thư viện ngoài vì chỉ dùng thư viện có sẵn.

5. Hướng dẫn chạy chương trình:
    - Tải đầy đủ mã nguồn từ repository GitHub (hoặc clone repo về máy)
    - Mở terminal hoặc command prompt
    - Di chuyển vào thư mục chứa mã nguồn
    - Chạy chương trình: chạy file Inverted_Indexes.py

* Hướng dẫn sử dụng giao diện:    
    - Chọn thư mục chứa tài liệu: Nhấn nút Select Folder rồi chọn thư mục có chứa các file văn bản cần lập chỉ mục (ví dụ folder Data_Test thuộc project).
    - Tạo chỉ mục nghịch đảo: Nhấn nút Inverted Indexes để chương trình quét thư mục và tạo chỉ mục. Nhấn nút Show Inverted Indexes để mở cửa sổ xem DocTable và TermTable.
    - Tìm kiếm theo từ khóa đơn: Nhấn nút Find, nhập thông tin và bấm Find để tìm top N tài liệu phù hợp. Kết quả sẽ hiển thị bên dưới.
    - Tìm kiếm theo file danh sách từ khóa: Nhấn nút WordFile Search để hiện khung chọn file chứa danh sách từ khóa + trọng số (ví dụ file WordFile_Test). Nhập số lượng kết quả Top N và bấm Search from File, kết quả sẽ hiển thị bên dưới.

6. Ví dụ input và output:
* Input: 
    - Folder Data_Test trong dự án dùng cho Inverted Indexes
    - File stoplist.txt chứa danh sách các stopword
    - File WordFile_Text.txt dùng cho chức năng WordFile Search
* Output:
    - DocTable và TermTable được lưu ở file doc_table.csv và term_table.csv

