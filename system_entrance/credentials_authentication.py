"""Implementation for some tests that are performed when a system login is performed. 
"""



"""for username authentication use :
    Minimum and maximum length: Set a minimum and maximum length for the username string to prevent users from choosing usernames that are too short or too long. The minimum length should be long enough to provide some degree of security, such as 6-8 characters, while the maximum length should not be too long to avoid potential issues with database fields.

    Character set: Limit the character set for the username string to alphanumeric characters (a-z, A-Z, and 0-9) and special characters that are commonly allowed in usernames, such as underscore (_), hyphen (-), or period (.) characters. Avoid allowing spaces or other special characters that could be used to exploit vulnerabilities.

    Case sensitivity: Decide whether or not your usernames will be case-sensitive. Allowing both upper and lower case characters can make usernames harder to guess, but it also makes it more difficult for users to remember their usernames if they are not consistent.

    Unique usernames: Ensure that usernames are unique across the system to avoid potential issues with collisions or conflicts. You can enforce uniqueness at the database level or through other means, such as using a hashing algorithm to generate unique usernames.

    Avoid personally identifiable information: Avoid using personally identifiable information (PII) such as the user's full name, email address, or social security number as the username. This can help protect user privacy and prevent potential security issues if the PII is compromised.

    Avoid bad usernames by blacklist from https://github.com/marteinn/The-Big-Username-Blocklist/blob/669ca49e0c0c72fed546566db3e1558ad8d5aa02/list.json
        filter only those passed all pretests and check them.
    
    Consider implementing two-factor authentication (2FA) or multi-factor authentication (MFA) to enhance the security of usernames and passwords.
    
    
    Consider use with UserName class instead!!!

"""

"""
for password authentication use:
    Minimum and maximum length: Set a minimum and maximum length for passwords to prevent users from choosing passwords that are too short or too long. The minimum length should be long enough to provide some degree of security, such as 8-10 characters, while the maximum length should not be too long to avoid potential issues with database fields.

    Character set: Encourage users to choose complex passwords that include a mix of upper and lowercase letters, numbers, and special characters. Avoid common dictionary words and phrases or easily guessable patterns, such as "password123" or "12345678".

    Avoid personally identifiable information: Discourage users from using personally identifiable information (PII) such as their name, birthdate, or social security number as part of their password. This can help protect user privacy and prevent potential security issues if the PII is compromised.

    Password expiration and history: Consider implementing a password expiration policy that requires users to change their passwords every few months. Also, consider keeping a history of previous passwords and prevent users from reusing them.

    Two-factor authentication (2FA) or multi-factor authentication (MFA): Encourage or require users to enable 2FA or MFA to add an additional layer of security to their account.

    Password hashing and salting: Use secure password hashing algorithms, such as bcrypt or Argon2, to store passwords securely in your database. Salting the passwords before hashing them can further enhance their security.

    Educate users: Educate your users on the importance of choosing secure passwords and provide guidelines for creating strong passwords. Consider using a password strength meter to help users choose strong passwords.
consider use with Password class instead!!!
"""

class CredentialsAuthenticator:
    """A collection of functions that help verify the username and password
    when logging into the system.
    """
    @staticmethod
    def is_valid_username(username: str) -> bool:
        """Checks if the username is valid by rules written in the

        Args:
            username (str): username to be checked.

        Returns:
            bool: True if username is valid, False otherwise.
        """
        pass
    @staticmethod
    def is_bad_username(username: str) -> bool:
        """
        """
        pass
    @staticmethod
    def is_username_exists(username: str) -> bool:
        pass
    @staticmethod
    def is_valid_password(password: str) -> bool:
        pass